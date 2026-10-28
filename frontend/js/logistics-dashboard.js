/**
 * ═══════════════════════════════════════════════════════════════════
 * LOGISTICS CONTROL TOWER & FLEET CONTROLLER — V6 LOGISTICS
 * Autonomous Logistics Platform (Fast-Path, ReAct Agent & Geospatial)
 * ═══════════════════════════════════════════════════════════════════
 */

let allShipments = [];
let selectedShipmentId = null;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if on client dashboard page
    if (document.getElementById('panel-logistics')) {
        console.log('🚚 Logistics Control Tower Controller Initialized');
    }
});

/**
 * Load and render Logistics Control Tower tab
 */
async function loadLogisticsTab() {
    try {
        await Promise.all([
            loadLogisticsKPIs(),
            loadShipmentsList(),
            loadExceptionFeed()
        ]);
    } catch (err) {
        console.error('Failed to load logistics tab:', err);
    }
}

/**
 * Fetch and update Control Tower KPIs
 */
async function loadLogisticsKPIs() {
    try {
        const data = await API.getLogisticsDashboard();
        if (!data || !data.metrics) return;
        const m = data.metrics;

        const setEl = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setEl('kpiTotalShipments', m.total_shipments || 0);
        setEl('kpiInTransit', m.active_in_transit || 0);
        setEl('kpiExceptions', m.active_exceptions || 0);
        setEl('kpiDelivered', m.delivered || 0);
        setEl('kpiZones', m.active_delivery_zones || 0);
        setEl('kpiModelStatus', 'GB Trees (Active)');

        // Exception badge in sidebar
        const badge = document.getElementById('shipmentAlertBadge');
        if (badge) {
            if (m.active_exceptions > 0) {
                badge.textContent = m.active_exceptions;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (err) {
        console.warn('Could not load logistics KPIs:', err);
    }
}

/**
 * Fetch and render Shipments Table
 */
async function loadShipmentsList() {
    const tableBody = document.getElementById('shipmentsTableBody');
    if (!tableBody) return;

    try {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:#94a3b8;">Loading active fleet telemetry...</td></tr>`;

        const carrierFilter = document.getElementById('shipmentCarrierFilter')?.value || '';
        const statusFilter = document.getElementById('shipmentStatusFilter')?.value || '';
        const searchInput = document.getElementById('shipmentSearchInput')?.value.trim().toLowerCase() || '';

        const params = { limit: 100 };
        if (carrierFilter) params.carrier = carrierFilter;
        if (statusFilter) params.status = statusFilter;

        const data = await API.getShipments(params);
        allShipments = data.shipments || [];

        let filtered = allShipments;
        if (searchInput) {
            filtered = filtered.filter(s => 
                (s.tracking_number && s.tracking_number.toLowerCase().includes(searchInput)) ||
                (s.carrier_tracking_id && s.carrier_tracking_id.toLowerCase().includes(searchInput)) ||
                (s.origin_city && s.origin_city.toLowerCase().includes(searchInput)) ||
                (s.destination_city && s.destination_city.toLowerCase().includes(searchInput))
            );
        }

        if (filtered.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:#94a3b8;">No shipments found matching filters.</td></tr>`;
            return;
        }

        tableBody.innerHTML = filtered.map(s => {
            const carrierClass = `carrier-${(s.carrier || 'fedex').toLowerCase()}`;
            const statusClass = `status-${(s.status || 'in_transit').toLowerCase()}`;
            const isSelected = s.id === selectedShipmentId ? 'selected' : '';
            const isPulse = s.status === 'in_transit' || s.status === 'out_for_delivery';
            const isException = s.has_exception || s.status === 'exception';

            const originCity = s.origin_city || (typeof s.origin === 'object' ? s.origin?.city : s.origin) || 'Origin';
            const destCity = s.destination_city || (typeof s.destination === 'object' ? s.destination?.city : s.destination) || 'Destination';
            const locName = (typeof s.current_location === 'object' ? s.current_location?.name : s.current_location) || originCity || 'In Transit';
            const trackingNo = s.tracking_number || s.shipment_id || ('SHP-' + s.id);
            const estHours = s.estimated_delivery_hours ?? s.transit_time_hours;

            return `
                <tr class="${isSelected}" onclick="inspectShipment(${s.id})">
                    <td style="font-weight:700;letter-spacing:0.02em;">
                        <span style="color:#e2e8f0;">${trackingNo}</span>
                        ${s.carrier_tracking_id ? `<br><span style="font-size:0.7rem;color:#94a3b8;">${s.carrier_tracking_id}</span>` : ''}
                    </td>
                    <td>
                        <span class="carrier-pill ${carrierClass}">${s.carrier || 'FedEx'}</span>
                    </td>
                    <td>
                        <span style="color:#cbd5e1;">${originCity}</span>
                        <span style="color:#6366f1;font-weight:bold;"> &rarr; </span>
                        <span style="color:#f8fafc;font-weight:600;">${destCity}</span>
                    </td>
                    <td>
                        <span style="font-size:0.8rem;color:#94a3b8;">${locName}</span>
                    </td>
                    <td>
                        <span class="status-pill ${statusClass}">
                            ${isPulse ? '<span class="pulse-dot"></span>' : ''}
                            ${isException ? '⚠️ ' : ''}
                            ${formatStatusLabel(s.status)}
                        </span>
                    </td>
                    <td>
                        <span style="color:#38bdf8;font-weight:600;">${estHours ? estHours.toFixed(1) + ' hrs' : '--'}</span>
                        <span style="font-size:0.7rem;color:#64748b;"> (SLA: ${s.sla_delivery_hours || 48}h)</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); inspectShipment(${s.id})" style="padding:3px 8px;font-size:0.72rem;">Inspect</button>
                    </td>
                </tr>
            `;
        }).join('');

        // Automatically inspect first shipment if none selected
        if (!selectedShipmentId && filtered.length > 0) {
            inspectShipment(filtered[0].id);
        }

    } catch (err) {
        console.error('Error rendering shipments list:', err);
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:#ef4444;">Failed to load fleet data: ${err.message}</td></tr>`;
    }
}

/**
 * Format status string to readable title
 */
function formatStatusLabel(st) {
    if (!st) return 'Pending';
    return st.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

/**
 * Inspect single shipment and load its milestone timeline
 */
async function inspectShipment(shipmentId) {
    selectedShipmentId = shipmentId;

    // Highlight selected row
    const rows = document.querySelectorAll('#shipmentsTableBody tr');
    rows.forEach(r => r.classList.remove('selected'));

    const timelineContainer = document.getElementById('shipmentTimelineContent');
    const waybillEl = document.getElementById('selectedWaybillTitle');
    const headerEl = document.getElementById('selectedShipmentHeader');

    if (waybillEl) waybillEl.textContent = `Waybill #SHP-${shipmentId}`;
    if (timelineContainer) {
        timelineContainer.innerHTML = `<div style="text-align:center;padding:1.5rem;color:#94a3b8;">Loading telemetry events...</div>`;
    }

    try {
        const [shipmentData, timelineData] = await Promise.all([
            API.getShipment(shipmentId),
            API.getShipmentTimeline(shipmentId)
        ]);

        const s = shipmentData.shipment || shipmentData;
        const events = timelineData.timeline || [];

        const originCity = s.origin_city || (typeof s.origin === 'object' ? s.origin?.city : s.origin) || 'Origin';
        const destCity = s.destination_city || (typeof s.destination === 'object' ? s.destination?.city : s.destination) || 'Destination';
        const estHours = s.estimated_delivery_hours ?? s.transit_time_hours;

        if (headerEl) {
            headerEl.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
                    <div>
                        <span class="carrier-pill carrier-${(s.carrier||'fedex').toLowerCase()}">${s.carrier}</span>
                        <span class="status-pill status-${(s.status||'in_transit').toLowerCase()}" style="margin-left:6px;">${formatStatusLabel(s.status)}</span>
                    </div>
                    <span style="font-size:0.75rem;color:#94a3b8;">Service: <strong>${s.service_type || 'Standard'}</strong></span>
                </div>
                <div style="font-size:0.8rem;color:#cbd5e1;line-height:1.4;">
                    <strong>Route:</strong> ${originCity} &rarr; ${destCity}<br>
                    <strong>ML Predicted Transit:</strong> <span style="color:#38bdf8;font-weight:700;">${estHours ? estHours.toFixed(1) + ' hours' : 'Calculating'}</span>
                </div>
            `;
        }

        if (timelineContainer) {
            if (events.length === 0) {
                timelineContainer.innerHTML = `<div style="padding:1rem;color:#94a3b8;font-size:0.8rem;">No milestone events recorded yet.</div>`;
                return;
            }

            timelineContainer.innerHTML = `
                <div class="timeline-track">
                    ${events.map((ev, idx) => {
                        const isDone = ev.event_type === 'DELIVERED';
                        const isWarn = ev.has_exception || ev.event_type.includes('EXCEPTION') || ev.event_type.includes('ATTEMPT');
                        const markerClass = isDone ? 'done' : (isWarn ? 'warn' : '');

                        const evTime = ev.timestamp ? new Date(ev.timestamp).toLocaleString([], {
                            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                        }) : '--';

                        return `
                            <div class="timeline-item">
                                <div class="timeline-marker ${markerClass}">
                                    ${isDone ? '✓' : (isWarn ? '!' : '•')}
                                </div>
                                <div class="timeline-title">${formatStatusLabel(ev.event_type)}</div>
                                <div class="timeline-time">${evTime} — <span style="color:#6366f1;">${ev.location || 'Checkpoint'}</span></div>
                                <div class="timeline-desc">${ev.description || ''}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }

    } catch (err) {
        console.error('Error loading shipment timeline:', err);
        if (timelineContainer) {
            timelineContainer.innerHTML = `<div style="color:#ef4444;font-size:0.8rem;">Failed to load timeline: ${err.message}</div>`;
        }
    }
}

/**
 * Load Active Exceptions Feed
 */
async function loadExceptionFeed() {
    const feedContainer = document.getElementById('exceptionFeedContent');
    if (!feedContainer) return;

    try {
        const data = await API.getShipmentExceptions();
        const exceptions = data.exceptions || [];

        if (exceptions.length === 0) {
            feedContainer.innerHTML = `
                <div style="text-align:center;padding:2rem 1rem;color:#10b981;font-size:0.82rem;">
                    ✓ Zero active exceptions! All carrier routes operational.
                </div>
            `;
            return;
        }

        feedContainer.innerHTML = exceptions.map(ex => {
            const sentimentLabel = ex.customer_sentiment || 'frustrated';
            const isVery = sentimentLabel.includes('very') || sentimentLabel.includes('Very');

            return `
                <div class="exception-alert-card">
                    <div class="exc-header">
                        <span class="exc-waybill">${ex.tracking_number}</span>
                        <span class="exc-sentiment ${isVery ? 'frustrated' : 'neutral'}">
                            ${isVery ? '😡 Frustrated' : '😟 Concerned'}
                        </span>
                    </div>
                    <div class="exc-details">
                        <strong>${ex.carrier}</strong> &bull; ${ex.origin_city} &rarr; ${ex.destination_city}<br>
                        <span style="color:#f87171;font-weight:600;">Issue: ${ex.exception_reason || 'Delayed transit'}</span>
                    </div>
                    <button class="exc-action-btn" onclick="inspectShipment(${ex.id})">
                        Resolve &amp; View Empathetic Plan &rarr;
                    </button>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.warn('Could not load exceptions feed:', err);
    }
}

/**
 * Freight & ML ETA Interactive Calculator
 */
async function runFreightAndETACalculator() {
    const origin = document.getElementById('calcOriginCity')?.value || 'New York';
    const dest = document.getElementById('calcDestCity')?.value || 'Los Angeles';
    const carrier = document.getElementById('calcCarrier')?.value || 'FedEx';
    const service = document.getElementById('calcService')?.value || 'standard';
    const weight = parseFloat(document.getElementById('calcWeight')?.value || '5.0');

    const resDist = document.getElementById('resCalcDistance');
    const resETA = document.getElementById('resCalcETA');
    const resRate = document.getElementById('resCalcRate');

    if (resDist) resDist.textContent = '...';
    if (resETA) resETA.textContent = '...';
    if (resRate) resRate.textContent = '...';

    try {
        const [etaResp, quoteResp] = await Promise.all([
            API.predictETA({
                origin_city: origin,
                destination_city: dest,
                carrier: carrier,
                service_type: service
            }),
            API.calculateFreight({
                origin_city: origin,
                destination_city: dest,
                carrier: carrier,
                service_type: service,
                weight_kg: weight
            })
        ]);

        if (resDist) resDist.textContent = (quoteResp.distance_km || etaResp.distance_km || 0).toFixed(0) + ' km';
        if (resETA) resETA.textContent = (etaResp.predicted_transit_hours || 0).toFixed(1) + ' hrs';
        if (resRate) resRate.textContent = '$' + (quoteResp.total_quote_usd || 0).toFixed(2);

    } catch (err) {
        console.error('Calculation error:', err);
        alert('Calculation failed: ' + err.message);
    }
}

/**
 * Load and render Delivery Zones Tab
 */
async function loadDeliveryZonesTab() {
    const grid = document.getElementById('deliveryZonesGrid');
    if (!grid) return;

    try {
        grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:3rem;color:#94a3b8;">Loading operational delivery zones...</div>`;
        const data = await API.getDeliveryZones();
        const zones = data.zones || [];

        if (zones.length === 0) {
            grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:3rem;color:#94a3b8;">No delivery zones configured yet.</div>`;
            return;
        }

        grid.innerHTML = zones.map(z => {
            const zoneName = z.zone_name || z.name || 'Regional Zone';
            const code = z.zone_code || 'ZN';
            const centerLat = z.center_lat ?? 0;
            const centerLng = z.center_lng ?? 0;
            const radius = z.radius_km ?? 50;
            const baseHours = z.base_delivery_hours ?? 24;
            const avgHours = z.avg_delivery_hours ?? z.average_delivery_hours ?? baseHours;
            const basePrice = z.base_price ?? z.base_cost ?? 15.0;
            const successRate = z.delivery_success_rate ?? z.success_rate ?? 0.95;
            const currency = z.currency || 'USD';

            const latStr = typeof centerLat === 'number' ? centerLat.toFixed(2) : centerLat;
            const lngStr = typeof centerLng === 'number' ? centerLng.toFixed(2) : centerLng;

            return `
            <div class="zone-card">
                <div class="zone-card-header">
                    <div>
                        <span class="zone-code">${code}</span>
                        <div class="zone-name">${zoneName}</div>
                    </div>
                    <span class="status-pill status-delivered">${z.is_serviceable !== false ? 'Active Service Hub' : 'Inactive'}</span>
                </div>
                <div style="font-size:0.76rem;color:#94a3b8;margin-bottom:0.5rem;">
                    Hub Coordinates: [${latStr}&deg; N, ${lngStr}&deg; W] &bull; Radius: ${radius} km
                </div>
                <div class="zone-metrics">
                    <div class="zone-m-item">
                        <div class="v">${baseHours.toFixed(0)}h</div>
                        <div class="l">Base SLA Target</div>
                    </div>
                    <div class="zone-m-item">
                        <div class="v">${avgHours.toFixed(1)}h</div>
                        <div class="l">Historical Avg</div>
                    </div>
                    <div class="zone-m-item">
                        <div class="v">$${basePrice.toFixed(2)}</div>
                        <div class="l">Base Dispatch Fee (${currency})</div>
                    </div>
                    <div class="zone-m-item">
                        <div class="v">${(successRate * 100).toFixed(1)}%</div>
                        <div class="l">Success Rate</div>
                    </div>
                </div>
            </div>
            `;
        }).join('');

    } catch (err) {
        console.error('Error loading zones:', err);
        grid.innerHTML = `<div style="grid-column:1/-1;color:#ef4444;text-align:center;">Failed to load zones: ${err.message}</div>`;
    }
}

// Attach to window object
window.LogisticsDashboard = {
    loadTab: loadLogisticsTab,
    loadShipments: loadShipmentsList,
    inspectShipment: inspectShipment,
    runCalculator: runFreightAndETACalculator,
    loadZonesTab: loadDeliveryZonesTab
};
