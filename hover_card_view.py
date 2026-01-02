"""
Hover Card View Module for OpTrack Dashboard
Renders unit breakdown list with hover-to-reveal detail cards
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render_hover_breakdown_list(df, get_unit_icon_html_func, timezone):
    """
    Render breakdown list with hover-to-reveal detail cards
    
    Args:
        df: DataFrame with unit breakdown data
        get_unit_icon_html_func: Function to get unit icon HTML
        timezone: Timezone for date calculations
    """
    
    # CSS Styling
    css = """
    <style>
    .hover-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 0;
    }
    
    .unit-row {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px 20px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .unit-row:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
        transform: translateX(4px);
    }
    
    .unit-summary {
        display: flex;
        align-items: center;
        gap: 16px;
        justify-content: space-between;
    }
    
    .unit-left {
        display: flex;
        align-items: center;
        gap: 14px;
        flex: 1;
    }
    
    .unit-icon-box {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    
    .unit-icon-box img {
        width: 40px;
        height: 40px;
        object-fit: contain;
    }
    
    .unit-main-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .unit-id {
        font-size: 15px;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.01em;
    }
    
    .unit-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 13px;
        color: #6B7280;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .meta-icon {
        width: 14px;
        height: 14px;
        opacity: 0.7;
    }
    
    .unit-status {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
    }
    
    .status-badge-hover {
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        background: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FECACA;
    }
    
    .duration-text {
        font-size: 14px;
        font-weight: 700;
        color: #EF4444;
    }
    
    /* HOVER DETAIL CARD - LARGER MODAL STYLE */
    .hover-detail {
        position: fixed;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 700px;
        max-height: 85vh;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        display: none;
        padding: 0;
        overflow: hidden;
    }
    
    .unit-row:hover .hover-detail {
        display: block;
        animation: modalFadeIn 0.25s ease-out;
    }
    
    @keyframes modalFadeIn {
        from {
            opacity: 0;
            transform: translate(-50%, -48%);
        }
        to {
            opacity: 1;
            transform: translate(-50%, -50%);
        }
    }
    
    /* Modal Backdrop */
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9998;
        display: none;
    }
    
    .unit-row:hover .modal-backdrop {
        display: block;
        animation: backdropFadeIn 0.25s ease-out;
    }
    
    @keyframes backdropFadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .detail-header {
        background: #FFFFFF;
        color: #111827;
        padding: 24px;
        border-bottom: 1px solid #E5E7EB;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .detail-unit-name {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
    }
    
    .detail-body {
        padding: 0;
        max-height: calc(85vh - 80px);
        overflow-y: auto;
    }
    
    .detail-content-wrapper {
        display: flex;
        gap: 24px;
        padding: 24px;
    }
    
    .detail-left {
        flex: 0 0 220px;
    }
    
    .detail-right {
        flex: 1;
    }
    
    .unit-photo-box {
        width: 220px;
        height: 165px;
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-bottom: 16px;
    }
    
    .unit-photo-box img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .detail-section {
        margin-bottom: 20px;
    }
    
    .detail-section:last-child {
        margin-bottom: 0;
    }
    
    .detail-label {
        font-size: 12px;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 8px;
    }
    
    .detail-text {
        font-size: 14px;
        color: #374151;
        line-height: 1.6;
    }
    
    /* CSS BAR CHART */
    .history-chart {
        display: flex;
        gap: 16px;
        align-items: flex-end;
        height: 120px;
        padding: 12px;
        background: #F9FAFB;
        border-radius: 8px;
    }
    
    .chart-bar-vertical {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
    }
    
    .bar-column {
        width: 100%;
        height: 80px;
        background: #E5E7EB;
        border-radius: 6px 6px 0 0;
        position: relative;
        display: flex;
        align-items: flex-end;
    }
    
    .bar-fill-vertical {
        width: 100%;
        background: linear-gradient(180deg, #60A5FA, #3B82F6);
        border-radius: 6px 6px 0 0;
        transition: height 0.4s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 13px;
    }
    
    .bar-value {
        font-size: 11px;
        font-weight: 700;
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* ACTION LIST */
    .action-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .action-item {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        padding: 10px 12px;
        background: #F9FAFB;
        border-radius: 8px;
        border-left: 3px solid #F59E0B;
    }
    
    .action-icon {
        width: 16px;
        height: 16px;
        color: #F59E0B;
        flex-shrink: 0;
        margin-top: 1px;
    }
    
    .action-text {
        font-size: 13px;
        color: #374151;
        line-height: 1.5;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        background: #F9FAFB;
        padding: 12px;
        border-radius: 8px;
    }
    
    .info-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .info-item-label {
        font-size: 11px;
        color: #6B7280;
        font-weight: 500;
    }
    
    .info-item-value {
        font-size: 14px;
        color: #111827;
        font-weight: 600;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    if df.empty:
        st.markdown('<div style="text-align:center;padding:40px;color:#9CA3AF;">No breakdown units</div>', unsafe_allow_html=True)
        return
    
    # Icons
    location_icon = '<svg viewBox="0 0 24 24" fill="#EF4444" width="14" height="14"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'
    clock_icon = '<svg viewBox="0 0 24 24" fill="#8B5CF6" width="14" height="14"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>'
    alert_icon = '<svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>'
    
    # Container
    st.markdown('<div class="hover-container">', unsafe_allow_html=True)
    
    # Sort by start date
    df_sorted = df.sort_values('start_date', ascending=False).reset_index(drop=True)
    
    for idx, row in df_sorted.iterrows():
        unit_id = row.get('unit_code', 'UNKNOWN')
        location = row.get('pit', '-')
        status = row.get('current_status', 'Open')
        event_type = str(row.get('event_type', 'Breakdown'))[:30]
        
        # Duration calculation
        if status == 'Open' and pd.notna(row.get('start_date')):
            start_iso = row['start_date'].strftime('%Y-%m-%dT%H:%M:%S')
            duration_html = f'<span class="duration-text live-duration" data-start="{start_iso}">calculating...</span>'
            
            # Calculate for display in detail
            now = datetime.now(timezone)
            start = row['start_date']
            if start.tzinfo is None:
                start = timezone.localize(start)
            diff_hours = (now - start).total_seconds() / 3600
        else:
            dur_val = f"{row['total_duration_hours']:.1f}h" if pd.notna(row.get('total_duration_hours')) else '0h'
            duration_html = f'<span class="duration-text">{dur_val}</span>'
            diff_hours = row.get('total_duration_hours', 0)
        
        start_time = row['start_date'].strftime('%d %b %H:%M') if pd.notna(row.get('start_date')) else '-'
        
        # Generate icon
        unit_icon = get_unit_icon_html_func(unit_id, 40)
        
        # Notes/Actions
        notes = str(row.get('noted', '')) if pd.notna(row.get('noted')) else ''
        actions = []
        if notes.strip():
            actions.append(notes)
        else:
            actions.append("Monitor unit status")
            actions.append("Coordinate with maintenance team")
        
        # Mock history data (in real scenario, query from database)
        # For now, create mock data based on duration
        history_data = [
            {"label": "This Week", "count": 1, "max": 5},
            {"label": "This Month", "count": 2, "max": 10},
            {"label": "Last 3 Months", "count": 3, "max": 15}
        ]
        
        # Generate history chart HTML - VERTICAL BARS
        chart_html = ""
        for hist in history_data:
            percentage = (hist['count'] / hist['max']) * 100 if hist['max'] > 0 else 0
            bar_height = (hist['count'] / 5) * 80  # Max 80px height
            chart_html += f'''
            <div class="chart-bar-vertical">
                <div class="bar-column">
                    <div class="bar-fill-vertical" style="height: {bar_height}px">
                        {hist['count']}
                    </div>
                </div>
                <div style="font-size:11px;color:#6B7280;font-weight:500;">{hist['label']}</div>
            </div>
            '''
        
        # Generate action items HTML
        action_html = ""
        for action in actions[:3]:  # Limit to 3 actions
            action_html += f'''
            <div class="action-item">
                <div class="action-icon">{alert_icon}</div>
                <div class="action-text">{action}</div>
            </div>
            '''
        
        # Get larger unit icon for photo
        unit_photo = get_unit_icon_html_func(unit_id, 160)
        
        # Render the row with hover detail
        html = f'''
        <div class="unit-row">
            <!-- Modal Backdrop -->
            <div class="modal-backdrop"></div>
            
            <div class="unit-summary">
                <div class="unit-left">
                    <div class="unit-icon-box">{unit_icon}</div>
                    <div class="unit-main-info">
                        <div class="unit-id">{unit_id}</div>
                        <div class="unit-meta">
                            <span class="meta-item">
                                <span class="meta-icon">{location_icon}</span>
                                {location}
                            </span>
                            <span class="meta-item">
                                <span class="meta-icon">{clock_icon}</span>
                                {start_time}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="unit-status">
                    <span class="status-badge-hover">{status.upper()}</span>
                    {duration_html}
                </div>
            </div>
            
            <!-- HOVER DETAIL CARD - MODAL STYLE -->
            <div class="hover-detail">
                <div class="detail-header">
                    <div class="detail-unit-name">{unit_id} - {event_type}</div>
                </div>
                <div class="detail-body">
                    <div class="detail-content-wrapper">
                        <!-- LEFT: Unit Photo -->
                        <div class="detail-left">
                            <div class="unit-photo-box">{unit_photo}</div>
                            <div class="detail-section">
                                <div class="detail-label">Unit Info</div>
                                <div class="detail-text"><strong>Unit No:</strong> {unit_id}</div>
                                <div class="detail-text"><strong>Location:</strong> {location}</div>
                                <div class="detail-text"><strong>Time:</strong> {start_time}</div>
                            </div>
                        </div>
                        
                        <!-- RIGHT: Details -->
                        <div class="detail-right">
                            <!-- Status Cards -->
                            <div class="info-grid">
                                <div class="info-item">
                                    <div class="info-item-label">Current Breakdown</div>
                                    <div class="info-item-value">{event_type}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-item-label">Duration</div>
                                    <div class="info-item-value">{diff_hours:.1f}h</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-item-label">Status</div>
                                    <div class="info-item-value" style="color:#EF4444">{status.upper()}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-item-label">Started</div>
                                    <div class="info-item-value">{start_time}</div>
                                </div>
                            </div>
                            
                            <!-- History Chart -->
                            <div class="detail-section">
                                <div class="detail-label">Riwayat 30 Hari Terakhir (Total: 3)</div>
                                <div class="history-chart">
                                    {chart_html}
                                </div>
                            </div>
                            
                            <!-- Kebutuhan Section -->
                            <div class="detail-section">
                                <div class="detail-label">Kebutuhan</div>
                                <div class="action-list">
                                    {action_html}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        st.markdown(html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
