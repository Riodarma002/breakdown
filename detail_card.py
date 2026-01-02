"""
Breakdown Detail Card Module - Simplified Version
Shows detailed breakdown info in an expandable card
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

TIMEZONE = pytz.timezone('Asia/Makassar')


def calculate_analytics(df, unit_code):
    """Calculate analytics for a specific unit"""
    now = datetime.now(TIMEZONE)
    unit_history = df[df['unit_code'] == unit_code].copy()
    
    total_breakdowns = len(unit_history)
    
    # MTTR
    ready_events = unit_history[unit_history['current_status'] == 'Ready']
    mttr = ready_events['total_duration_hours'].mean() if not ready_events.empty and 'total_duration_hours' in ready_events.columns else 0
    
    # Days since last
    if not unit_history.empty and 'start_date' in unit_history.columns:
        last_bd = unit_history['start_date'].max()
        if pd.notna(last_bd):
            if last_bd.tzinfo is None:
                last_bd = TIMEZONE.localize(last_bd)
            days_since = (now - last_bd).days
        else:
            days_since = None
    else:
        days_since = None
    
    # Frequency (30 days)
    thirty_days_ago = now - timedelta(days=30)
    recent = unit_history[unit_history['start_date'] >= thirty_days_ago.replace(tzinfo=None)]
    frequency_30d = len(recent)
    
    # Reliability index
    freq_penalty = min(frequency_30d * 10, 50)
    mttr_penalty = min(mttr * 5, 50) if mttr else 0
    reliability = max(0, 100 - freq_penalty - mttr_penalty)
    
    # MTTR comparison
    all_ready = df[df['current_status'] == 'Ready']
    if not all_ready.empty and 'total_duration_hours' in all_ready.columns:
        overall_mttr = all_ready['total_duration_hours'].mean()
        mttr_comparison = ((mttr - overall_mttr) / overall_mttr * 100) if overall_mttr > 0 else 0
    else:
        mttr_comparison = 0
    
    # Recommendation
    if frequency_30d >= 4:
        recommendation = f"Unit breakdown sering ({frequency_30d}x/bulan). Perlu inspeksi menyeluruh."
    elif mttr > 5:
        recommendation = f"Waktu perbaikan lama ({mttr:.1f}h). Evaluasi spare parts & skill teknisi."
    elif reliability < 50:
        recommendation = "Reliability rendah. Prioritaskan untuk maintenance improvement."
    else:
        recommendation = "Kondisi baik. Lanjutkan maintenance regular."
    
    return {
        'total_breakdowns': total_breakdowns,
        'mttr': mttr,
        'days_since_last': days_since,
        'frequency_30d': frequency_30d,
        'reliability': reliability,
        'mttr_comparison': mttr_comparison,
        'recommendation': recommendation
    }


def render_detail_popup(row, df, get_unit_icon_html_func):
    """Render detail card as Streamlit components (no raw HTML issues)"""
    
    unit_code = row['unit_code']
    status = row.get('current_status', 'Open')
    pit = row.get('pit', '-')
    event_type = row.get('event_type', '-')
    shift = row.get('shift', '-')
    notes = str(row.get('noted', '')) if pd.notna(row.get('noted')) else ''
    
    start_date = row.get('start_date')
    end_date = row.get('end_date')
    
    # Get analytics
    analytics = calculate_analytics(df, unit_code)
    
    # Card container style
    st.markdown("""
    <style>
    .detail-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.12);
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }
    .card-header {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        padding: 24px;
        border-bottom: 1px solid #E5E7EB;
    }
    .card-section {
        padding: 20px 24px;
        border-bottom: 1px solid #F3F4F6;
    }
    .card-section:last-child { border-bottom: none; }
    .section-label {
        font-size: 12px;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }
    .metric-box {
        text-align: center;
        padding: 16px;
        background: #F9FAFB;
        border-radius: 12px;
    }
    .metric-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
    }
    .metric-label {
        font-size: 11px;
        color: #6B7280;
        margin-top: 4px;
    }
    .insight-row {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 12px 16px;
        background: #FAFAFA;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .insight-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    .badge-good { background: #D1FAE5; color: #059669; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-warning { background: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .badge-danger { background: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
    .notes-box {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 4px solid #F59E0B;
        padding: 16px;
        border-radius: 8px;
        color: #78350F;
    }
    .rec-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid #3B82F6;
        padding: 16px;
        border-radius: 8px;
        color: #1E40AF;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with unit info
    col1, col2 = st.columns([1, 4])
    with col1:
        icon = get_unit_icon_html_func(unit_code, 80)
        st.markdown(f'<div style="background:#F1F5F9;border-radius:12px;padding:12px;text-align:center;">{icon}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {unit_code}")
        status_color = "#16A34A" if status == "Ready" else "#DC2626"
        st.markdown(f'<span style="background:{status_color}22;color:{status_color};padding:4px 12px;border-radius:16px;font-size:12px;font-weight:600;">{status}</span>', unsafe_allow_html=True)
        st.caption(f"📍 {pit} • 🔧 {event_type}")
    
    st.divider()
    
    # Info Grid
    st.markdown('<div class="section-label">📊 Informasi Breakdown</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("Start Date", start_date.strftime('%d %b %Y') if pd.notna(start_date) else '-')
        st.caption(start_date.strftime('%H:%M') if pd.notna(start_date) else '')
    
    with c2:
        st.metric("End Date", end_date.strftime('%d %b %Y') if pd.notna(end_date) else '-')
        st.caption(end_date.strftime('%H:%M') if pd.notna(end_date) else '')
    
    with c3:
        if status == 'Open' and pd.notna(start_date):
            st.metric("Duration", "Running...")
        else:
            dur_val = f"{row['total_duration_hours']:.1f}h" if pd.notna(row.get('total_duration_hours')) else '0h'
            st.metric("Duration", dur_val)
    
    with c4:
        st.metric("Shift", shift if shift else '-')
    
    # Notes
    if notes.strip():
        st.markdown('<div class="section-label">📝 Keterangan</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="notes-box">{notes}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Analytics
    st.markdown('<div class="section-label">📈 History Analytics (30 Hari)</div>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)
    
    with a1:
        st.metric("Total Breakdown", analytics['total_breakdowns'])
    with a2:
        st.metric("Avg Duration (MTTR)", f"{analytics['mttr']:.1f}h")
    with a3:
        st.metric("Days Since Last", analytics['days_since_last'] if analytics['days_since_last'] is not None else '-')
    
    st.divider()
    
    # Smart Insights
    st.markdown('<div class="section-label">🎯 Smart Insights</div>', unsafe_allow_html=True)
    
    # MTTR
    mttr_badge = "badge-good" if analytics['mttr_comparison'] <= 0 else "badge-warning"
    mttr_trend = "▼" if analytics['mttr_comparison'] <= 0 else "▲"
    st.markdown(f'''
    <div class="insight-row">
        <div class="insight-icon" style="background:#DBEAFE;">⚡</div>
        <div style="flex:1;">
            <div style="font-size:12px;color:#6B7280;">Mean Time To Repair (MTTR)</div>
            <div style="font-size:18px;font-weight:700;color:#111827;">
                {analytics['mttr']:.1f} jam
                <span class="{mttr_badge}">{mttr_trend} {abs(analytics['mttr_comparison']):.0f}% vs avg</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Frequency
    freq_badge = "badge-danger" if analytics['frequency_30d'] >= 4 else ("badge-warning" if analytics['frequency_30d'] >= 2 else "badge-good")
    freq_text = "TINGGI" if analytics['frequency_30d'] >= 4 else ("SEDANG" if analytics['frequency_30d'] >= 2 else "RENDAH")
    st.markdown(f'''
    <div class="insight-row">
        <div class="insight-icon" style="background:#FEE2E2;">📈</div>
        <div style="flex:1;">
            <div style="font-size:12px;color:#6B7280;">Breakdown Frequency (30d)</div>
            <div style="font-size:18px;font-weight:700;color:#111827;">
                {analytics['frequency_30d']} events
                <span class="{freq_badge}">{freq_text}</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Reliability
    rel_badge = "badge-good" if analytics['reliability'] >= 70 else ("badge-warning" if analytics['reliability'] >= 40 else "badge-danger")
    rel_text = "BAIK" if analytics['reliability'] >= 70 else ("MODERATE" if analytics['reliability'] >= 40 else "PERLU PERHATIAN")
    progress_color = "#22C55E" if analytics['reliability'] >= 70 else ("#F59E0B" if analytics['reliability'] >= 40 else "#EF4444")
    st.markdown(f'''
    <div class="insight-row">
        <div class="insight-icon" style="background:#D1FAE5;">🔮</div>
        <div style="flex:1;">
            <div style="font-size:12px;color:#6B7280;">Reliability Index</div>
            <div style="font-size:18px;font-weight:700;color:#111827;">
                {analytics['reliability']:.0f}/100
                <span class="{rel_badge}">{rel_text}</span>
            </div>
            <div style="height:8px;background:#E5E7EB;border-radius:4px;margin-top:8px;">
                <div style="height:100%;width:{analytics['reliability']}%;background:{progress_color};border-radius:4px;"></div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Recommendation
    st.markdown(f'<div class="rec-box">💡 <strong>Rekomendasi:</strong> {analytics["recommendation"]}</div>', unsafe_allow_html=True)
