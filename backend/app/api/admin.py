"""
Super Admin API — Autonomous Logistics Platform Administration
V6 Emotion-Gated Autonomous Logistics Platform

Only accessible by users with role = "super_admin".
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.conversation import Conversation
from app.models.message import Message
from app.middleware.jwt import get_current_user

# ★ V4/V6: Order, Product, KB, and Shipment model imports for cross-tenant browsing
try:
    from app.models.order import CustomerOrder
    from app.models.product_listing import ProductListing
    from app.models.knowledge_document import KnowledgeDocument
    from app.models.shipment import Shipment
except ImportError:
    CustomerOrder = None
    ProductListing = None
    KnowledgeDocument = None
    Shipment = None

router = APIRouter(prefix="/api/admin", tags=["Super Admin"])


# ═══════════════════════════════════════════════════════════════════
# RBAC GUARD — Super Admin only
# ═══════════════════════════════════════════════════════════════════

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency: require super_admin role"""
    if current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


# ═══════════════════════════════════════════════════════════════════
# FR-4.1: All-Account Management
# ═══════════════════════════════════════════════════════════════════

@router.get("/clients")
async def list_all_clients(
    search: Optional[str] = Query(None, description="Search by name, email, or URL"),
    status_filter: Optional[str] = Query(None, description="Filter by status: active, suspended"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """FR-4.1.1: List all client accounts with search and pagination"""
    query = db.query(Tenant)

    # Search filter (FR-4.1.2)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Tenant.name.ilike(search_term)) |
            (Tenant.store_url.ilike(search_term))
        )

    # Status filter
    if status_filter == "active":
        query = query.filter(Tenant.is_active == True)
    elif status_filter == "suspended":
        query = query.filter(Tenant.is_active == False)

    # Pagination
    total = query.count()
    tenants = query.order_by(Tenant.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    # Enrich with conversation counts
    results = []
    for tenant in tenants:
        tenant_data = tenant.to_dict()
        # Get owner info
        owner = db.query(User).filter(User.id == tenant.owner_id).first()
        tenant_data["owner_email"] = owner.email if owner else None
        tenant_data["owner_name"] = owner.get_display_name() if owner else None
        # Get conversation count
        conv_count = db.query(func.count(Conversation.id)).filter(
            Conversation.tenant_id == tenant.id
        ).scalar()
        tenant_data["conversation_count"] = conv_count
        results.append(tenant_data)

    return {
        "clients": results,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/clients/{client_id}")
async def get_client_detail(
    client_id: int,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """FR-4.1.6: View detailed client information"""
    tenant = db.query(Tenant).filter(Tenant.id == client_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Client not found")

    owner = db.query(User).filter(User.id == tenant.owner_id).first()

    # Get metrics
    conv_count = db.query(func.count(Conversation.id)).filter(
        Conversation.tenant_id == tenant.id
    ).scalar()
    escalated_count = db.query(func.count(Conversation.id)).filter(
        Conversation.tenant_id == tenant.id,
        Conversation.is_escalated == True
    ).scalar()
    msg_count = db.query(func.count(Message.id)).filter(
        Message.tenant_id == tenant.id
    ).scalar()

    # Knowledge documents
    kb_docs = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.tenant_id == tenant.id
    ).all() if KnowledgeDocument else []

    # Shipments count
    shipment_count = db.query(func.count(Shipment.id)).filter(
        Shipment.tenant_id == tenant.id
    ).scalar() if Shipment else 0

    return {
        "tenant": tenant.to_dict(),
        "owner": owner.to_dict() if owner else None,
        "knowledge_documents": [d.to_dict() for d in kb_docs],
        "metrics": {
            "total_conversations": conv_count,
            "escalated_conversations": escalated_count,
            "total_messages": msg_count,
            "escalation_rate": round(escalated_count / max(conv_count, 1) * 100, 1),
            "shipment_count": shipment_count,
            "order_count": db.query(func.count(CustomerOrder.id)).filter(CustomerOrder.tenant_id == tenant.id).scalar() if CustomerOrder else 0,
            "product_count": db.query(func.count(ProductListing.id)).filter(ProductListing.tenant_id == tenant.id).scalar() if ProductListing else 0,
            "kb_document_count": len(kb_docs),
        }
    }


@router.patch("/clients/{client_id}/status")
async def toggle_client_status(
    client_id: int,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """FR-4.1.3: Suspend or activate a client account"""
    tenant = db.query(Tenant).filter(Tenant.id == client_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Client not found")

    # Toggle status
    tenant.is_active = not tenant.is_active
    new_status = "active" if tenant.is_active else "suspended"

    # Also update the owner user status
    owner = db.query(User).filter(User.id == tenant.owner_id).first()
    if owner:
        owner.status = "active" if tenant.is_active else "suspended"

    db.commit()

    return {
        "message": f"Client {tenant.name} is now {new_status}",
        "client_id": client_id,
        "is_active": tenant.is_active,
        "status": new_status
    }


# ═══════════════════════════════════════════════════════════════════
# FR-4.2: System-Wide Analytics
# ═══════════════════════════════════════════════════════════════════

@router.get("/analytics")
async def system_analytics(
    days: int = Query(30, description="Analytics period in days"),
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """FR-4.2: System-wide analytics for the super admin"""
    since = datetime.utcnow() - timedelta(days=days)

    # Total clients (FR-4.2.2)
    total_clients = db.query(func.count(Tenant.id)).scalar()
    active_clients = db.query(func.count(Tenant.id)).filter(
        Tenant.is_active == True
    ).scalar()

    # Total conversations (FR-4.2.1)
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.created_at >= since
    ).scalar()

    # Escalation rate (FR-4.2.4)
    escalated = db.query(func.count(Conversation.id)).filter(
        Conversation.created_at >= since,
        Conversation.is_escalated == True
    ).scalar()

    # Average sentiment (FR-4.2.3)
    avg_sentiment = db.query(func.avg(Conversation.sentiment_score)).filter(
        Conversation.created_at >= since
    ).scalar()

    # Total messages
    total_messages = db.query(func.count(Message.id)).filter(
        Message.created_at >= since
    ).scalar()

    return {
        "period_days": days,
        "clients": {
            "total": total_clients,
            "active": active_clients,
            "suspended": total_clients - active_clients
        },
        "conversations": {
            "total": total_conversations,
            "escalated": escalated,
            "escalation_rate": round(escalated / max(total_conversations, 1) * 100, 1),
        },
        "messages": {
            "total": total_messages
        },
        "sentiment": {
            "average_score": round(avg_sentiment or 0.5, 3),
        }
    }


# ═══════════════════════════════════════════════════════════════════
# FR-4.3: Global Audit Logs (simplified — log API calls)
# ═══════════════════════════════════════════════════════════════════

@router.get("/logs")
async def get_audit_logs(
    event_type: Optional[str] = Query(None, description="Filter: login, signup, escalation"),
    client_id: Optional[int] = Query(None, description="Filter by client/tenant ID"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """FR-4.3: View audit logs (simplified: recent user activity)"""
    # Build query of recent user sessions as pseudo-audit log
    query = db.query(User).order_by(User.last_login.desc().nullslast())

    if client_id:
        query = query.filter(User.tenant_id == client_id)

    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    logs = []
    for user in users:
        logs.append({
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "status": user.status,
        })

    return {
        "logs": logs,
        "total": total,
        "page": page,
        "per_page": per_page
    }


# ═════════════════════════════════════════════════════════════════
# ★ V4: System Health (FR-4.4)
# ═════════════════════════════════════════════════════════════════

@router.get("/system-health")
async def system_health(
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """★ V4: Get system health metrics (super_admin only)."""
    import os

    # Database status
    try:
        db.execute(func.now())
        db_status = "connected"
    except Exception:
        db_status = "error"

    # Vector store sizes per tenant
    vs_sizes = []
    try:
        tenants = db.query(Tenant).all()
        for t in tenants[:20]:  # Limit to 20 for performance
            doc_count = 0
            try:
                from app.models.knowledge_document import KnowledgeDocument
                doc_count = db.query(func.count(KnowledgeDocument.id)).filter(
                    KnowledgeDocument.tenant_id == t.id
                ).scalar() or 0
            except Exception:
                pass
            vs_sizes.append({"tenant": t.name, "tenant_id": t.id, "documents": doc_count})
    except Exception:
        pass

    # BERT model status
    bert_loaded = False
    try:
        from app.nlp.transformer_sentiment import get_transformer_analyzer
        analyzer = get_transformer_analyzer()
        bert_loaded = analyzer is not None and getattr(analyzer, '_model', None) is not None
    except Exception:
        pass

    # LLM status
    llm_available = False
    try:
        from app.ai.llm import get_llm_service
        llm = get_llm_service()
        llm_available = llm.is_available()
    except Exception:
        pass

    return {
        "database": {"status": db_status, "pool_size": "active"},
        "vector_store": {"tenants": vs_sizes},
        "bert_model": {"loaded": bert_loaded},
        "llm": {"available": llm_available},
        "websocket": {"status": "active"},
    }


# ═════════════════════════════════════════════════════════════════
# ★ V4: Global Conversations (FR-4.5)
# ═════════════════════════════════════════════════════════════════

@router.get("/global-conversations")
async def global_conversations(
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    sentiment: Optional[str] = Query(None, description="Filter: positive, neutral, negative"),
    conv_status: Optional[str] = Query(None, description="Filter: active, escalated, resolved"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """★ V4: Get conversations across all tenants with filters."""
    query = db.query(Conversation)

    if tenant_id:
        query = query.filter(Conversation.tenant_id == tenant_id)
    if sentiment:
        query = query.filter(Conversation.current_sentiment == sentiment)
    if conv_status:
        query = query.filter(Conversation.status == conv_status)

    total = query.count()
    convos = query.order_by(Conversation.updated_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    results = []
    for c in convos:
        data = c.to_dict() if hasattr(c, 'to_dict') else {"id": c.id}
        # Enrich with enterprise company name
        tenant = db.query(Tenant).filter(Tenant.id == c.tenant_id).first()
        data["tenant_name"] = tenant.name if tenant else "Apex Global Logistics"
        results.append(data)

    return {
        "conversations": results,
        "total": total,
        "page": page,
        "per_page": per_page
    }


# ═════════════════════════════════════════════════════════════════
# ★ V4: Browse Tenant Orders / Products (FR-4.6)
# ═════════════════════════════════════════════════════════════════

@router.get("/orders")
@router.get("/tenant/{tenant_id}/orders")
async def admin_tenant_orders(
    tenant_id: Optional[int] = None,
    status: Optional[str] = Query(None, description="Filter by order/manifest status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """★ V4/V6: Get all orders/waybills for enterprise fleet operations."""
    if not CustomerOrder:
        return {"orders": [], "total": 0}

    query = db.query(CustomerOrder)
    if tenant_id:
        query = query.filter(CustomerOrder.tenant_id == tenant_id)
    if status:
        query = query.filter(CustomerOrder.status == status)

    total = query.count()
    orders = query.order_by(CustomerOrder.created_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return {
        "orders": [o.to_dict() for o in orders],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/products")
@router.get("/tenant/{tenant_id}/products")
async def admin_tenant_products(
    tenant_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """★ V4/V6: Get all products/freight SKUs for the enterprise fleet."""
    if not ProductListing:
        return {"products": [], "total": 0}

    query = db.query(ProductListing)
    if tenant_id:
        query = query.filter(ProductListing.tenant_id == tenant_id)

    total = query.count()
    products = query.offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return {
        "products": [p.to_dict() for p in products],
        "total": total,
        "page": page,
        "per_page": per_page
    }


# ═════════════════════════════════════════════════════════════════
# ★ V6: Cross-Tenant Global Logistics Overview
# ═════════════════════════════════════════════════════════════════

@router.get("/logistics-overview")
async def admin_logistics_overview(
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """★ V6: Get global logistics health, shipment counts, exceptions, and carrier breakdown across all tenants."""
    from app.models.shipment import Shipment
    from app.models.delivery_zone import DeliveryZone
    
    total_shipments = db.query(Shipment).count()
    active_in_transit = db.query(Shipment).filter(Shipment.status.in_(["in_transit", "out_for_delivery"])).count()
    exceptions = db.query(Shipment).filter(Shipment.has_exception == True).count()
    delivered = db.query(Shipment).filter(Shipment.status == "delivered").count()
    total_zones = db.query(DeliveryZone).count()
    
    # Carrier breakdown
    carriers = db.query(Shipment.carrier, func.count(Shipment.id)).group_by(Shipment.carrier).all()
    carrier_breakdown = {c or "Unknown": count for c, count in carriers}
    
    return {
        "status": "operational",
        "total_shipments": total_shipments,
        "active_in_transit": active_in_transit,
        "active_exceptions": exceptions,
        "delivered": delivered,
        "delivery_zones": total_zones,
        "carrier_breakdown": carrier_breakdown
    }
