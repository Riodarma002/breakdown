import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import base64
import os
import pytz
from table_view import render_breakdown_table, render_ready_table

# ========================================
# CONFIGURATION
# ========================================
TIMEZONE = pytz.timezone('Asia/Makassar')
st.set_page_config(
    page_title="OpTrack - Unit Breakdown Monitor",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================================
# MINIMALIST THEME CSS
# ========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #F8FAFB 0%, #F1F5F9 100%);
        font-family: 'Inter', -apple-system, sans-serif;
        transition: opacity 0.2s ease-in-out;
    }
    
    /* Prevent flash of blank content */
    .block-container {
        min-height: 100vh;
        background: linear-gradient(135deg, #F8FAFB 0%, #F1F5F9 100%);
    }
    
    /* Show loading background immediately */
    body {
        background: linear-gradient(135deg, #F8FAFB 0%, #F1F5F9 100%) !important;
    }
    
    /* Loading spinner styling */
    .stSpinner > div {
        border-color: #3B82F6 !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {display: none;}
    
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    [data-testid="stAppViewContainer"] > div:first-child {
        padding-top: 0 !important;
    }
    
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 2rem !important; 
        margin-top: 0 !important; 
    }
    
    /* Chart containers - let Plotly handle its own background */
    .js-plotly-plot, .plotly, .plot-container {
        background: #FFFFFF !important;
    }
    
    /* Streamlit chart wrapper styling */
    div[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:has(.chart-card-marker) > div {
        background: #FFFFFF !important;
    }
    
    /* Table Card Styling - Unified Container */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.table-card-marker) {
        background: #FFFFFF !important;
        
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        padding: 0 !important; /* Remove default padding to let header/table touch edges */
    }
    
    [data-testid="stVerticalBlockBorderWrapper"]:has(.table-card-marker) > div {
        background: #FFFFFF !important;
    }
    
    /* Adjust button position in the header */
    .table-header-btn button {
        height: 32px !important;
        padding: 0 16px !important;
        font-size: 0.8rem !important;
        line-height: 1 !important;
        min-height: 0px !important;
        margin-top: 2px !important;
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        
        border-radius: 12px !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        padding: 0 !important;
    }
    
    .filter-label {
        font-size: 0.65rem; font-weight: 600; color: #64748B;
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;
    }
    
    .metric-box {
        background: #FFFFFF;
        border-radius: 12px; padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        
    }
    
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #1E293B; }
    .metric-badge { font-size: 0.65rem; padding: 2px 8px; border-radius: 6px; font-weight: 500; margin-left: 6px; vertical-align: middle; }
    .metric-badge.blue { background: #DBEAFE; color: #1D4ED8; }
    .metric-badge.red { background: #FEE2E2; color: #DC2626; }
    .metric-badge.green { background: #DCFCE7; color: #16A34A; }
    .metric-label { font-size: 0.75rem; color: #94A3B8; margin-top: 2px; font-weight: 500; }
    
    .section-container {
        background: #FFFFFF;
        border-radius: 12px; padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        
        margin-bottom: 12px;
    }
    
    .section-header {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 0;
        margin-bottom: 2px;
    }
    
    .section-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .section-indicator.red { background: #EF4444; }
    .section-indicator.green { background: #10B981; }
    
    .section-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .section-count {
        background: #F1F5F9;
        color: #64748B;
        padding: 1px 6px;
        border-radius: 8px;
        font-size: 0.65rem;
        font-weight: 600;
    }
    
    /* UNIT LIST - Scrollable like dropdown */
    .unit-list {
        max-height: 380px;
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 4px;
    }
    
    .unit-list::-webkit-scrollbar { width: 8px; }
    .unit-list::-webkit-scrollbar-track { background: #1E293B; border-radius: 4px; }
    .unit-list::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
    .unit-list::-webkit-scrollbar-thumb:hover { background: #64748B; }
    
    /* REDESIGNED UNIT CARD */
    /* REDESIGNED UNIT CARD - Modern React-inspired Design */
    .unit-card {
        display: flex;
        gap: 16px;
        padding: 16px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-bottom: 12px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    
    .unit-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #3B82F6 0%, #60A5FA 100%);
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    
    .unit-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        border-color: #CBD5E1;
    }
    
    .unit-card:hover::before {
        opacity: 1;
    }
    
    /* Unit Image - Modern Container */
    .unit-img {
        width: 80px;
        height: 80px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 8px;
        transition: transform 0.2s ease;
    }
    
    .unit-card:hover .unit-img {
        transform: scale(1.05);
    }
    
    .unit-img img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    
    /* Unit Content */
    .unit-content {
        flex: 1;
        min-width:0;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .unit-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
    }
    
    .unit-name {
        font-size: 1rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    
    .status-badge {
        font-size: 0.625rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
        border: 1px solid;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .status-badge.open { 
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%); 
        color: #DC2626; 
        border-color: #FECACA;
    }
    
    .status-badge.ready { 
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); 
        color: #16A34A; 
        border-color: #BBF7D0;
    }
    
    /* Info Row with Icons - Enhanced */
    .unit-info-row {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: center;
    }
    
    .info-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8125rem;
        color: #475569;
        font-weight: 500;
        padding: 4px 0;
    }
    
    .info-icon {
        width: 16px;
        height: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #64748B;
    }
    
    .info-icon svg {
        width: 16px;
        height: 16px;
    }
    
    /* Duration Colors */
    .duration-red {
        color: #DC2626 !important;
        font-weight: 700 !important;
    }
    
    .duration-green {
        color: #16A34A !important;
        font-weight: 700 !important;
    }
    
    /* Notes Section - Modern Alert Style */
    .unit-notes {
        margin-top: 8px;
        padding: 10px 12px;
        background: linear-gradient(135deg, #FEF9C3 0%, #FEF3C7 100%);
        border-left: 3px solid #F59E0B;
        border-radius: 8px;
        font-size: 0.75rem;
        color: #78350F;
        line-height: 1.5;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .empty-state { text-align: center; padding: 30px 20px; color: #94A3B8; font-size: 0.85rem; }
    
    .chart-container {
        background: #FFFFFF;
        border-radius: 12px; padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        
        margin-bottom: 12px;
    }
    
    .chart-title { font-size: 0.8rem; font-weight: 600; color: #374151; margin-bottom: 12px; }
    
    /* Primary button styling */
    .stButton > button[data-testid="stBaseButton-primary"],
    .stButton > button[kind="primary"] { 
        background: #3B82F6 !important; 
        color: white !important; 
         
        border-radius: 8px !important; 
        font-size: 0.8rem !important; 
    }
    
    
    /* Secondary button styling - light gray background */
    .stButton > button[data-testid="stBaseButton-secondary"],
    .stButton > button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"],
    [class*="stButton"] button[data-testid="stBaseButton-secondary"],
    div[data-testid="stButton"] > button[data-testid="stBaseButton-secondary"] { 
        background: #F1F5F9 !important; 
        background-color: #F1F5F9 !important; 
        color: #475569 !important; 
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        border-radius: 8px !important; 
        font-size: 0.8rem !important; 
    }
    
    /* Override tertiary/minimal button type that may be used */
    .stButton > button[data-testid="stBaseButton-minimal"],
    button[data-testid="stBaseButton-minimal"],
    .stButton > button[data-testid="stBaseButton-tertiary"],
    button[data-testid="stBaseButton-tertiary"] { 
        background: #F1F5F9 !important; 
        background-color: #F1F5F9 !important; 
        color: #475569 !important; 
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        border-radius: 8px !important; 
    }
    
    /* Fallback for all buttons in stButton container */
    .stButton > button { 
        border-radius: 8px !important; 
        font-size: 0.8rem !important; 
    }
    
    /* Download button - white with border like reference */
    .stDownloadButton > button { 
        background: #FFFFFF !important; 
        color: #374151 !important; 
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important; 
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        padding: 8px 16px !important;
    }
    
    .stDownloadButton > button:hover { 
        background: #F9FAFB !important; 
        
    }
    
    /* Force download button to be white - all selectors */
    .stDownloadButton button,
    .stDownloadButton > button,
    [data-testid="stDownloadButton"] button,
    [data-testid="stDownloadButton"] > button,
    div.stDownloadButton button {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #374151 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    }
    
    .stSelectbox [data-baseweb="select"] { background-color: #FFFFFF !important; }
    .stSelectbox [data-baseweb="select"] > div { background-color: #FFFFFF !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important; border-radius: 8px !important; }
    .stSelectbox [data-baseweb="select"] > div:hover {  }
    .stSelectbox [data-baseweb="select"] span { color: #1E293B !important; font-size: 0.85rem !important; }
    .stSelectbox [data-baseweb="select"] div { color: #1E293B !important; }
    .stSelectbox svg { fill: #64748B !important; }
    
    [data-baseweb="popover"] { background-color: #FFFFFF !important; border-radius: 8px !important; box-shadow: 0 4px 16px rgba(0,0,0,0.12) !important; }
    [data-baseweb="menu"] { background-color: #FFFFFF !important; }
    [data-baseweb="menu"] li { background-color: #FFFFFF !important; color: #1E293B !important; font-size: 0.85rem !important; }
    [data-baseweb="menu"] li:hover { background-color: #F1F5F9 !important; }
    
    .stDateInput > div > div { background-color: #FFFFFF !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important; border-radius: 8px !important; }
    .stDateInput input { background-color: #FFFFFF !important; color: #1E293B !important;  font-size: 0.85rem !important; }
    .stDateInput svg { fill: #64748B !important; }
    
    /* Modern Table Design with Scroll */
   /* QUESTIFY-STYLE TABLE - EXACT REPLICA */
    
    /* Table wrapper - white box container */
    .table-section-wrapper {
        background: #FFFFFF;
        border-radius: 12px;
        
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        overflow: hidden;
        margin-top: 16px;
    }
    
    /* Table header section */
    .table-header-section {
        padding: 16px 24px;
        
        background: #FFFFFF;
    }
    
    .table-main-title {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin: 0;
    }
    
    /* Scroll container */
    .table-scroll-container {
        max-height: 500px;
        overflow-y: auto;
        overflow-x: auto;
        background: #FFFFFF;
    }
    
    .table-scroll-container::-webkit-scrollbar { 
        width: 6px; 
        height: 6px; 
    }
    
    .table-scroll-container::-webkit-scrollbar-track { 
        background: #FAFAFA; 
    }
    
    .table-scroll-container::-webkit-scrollbar-thumb { 
        background: #D1D5DB; 
        border-radius: 3px; 
    }
    
    .table-scroll-container::-webkit-scrollbar-thumb:hover { 
        background: #9CA3AF; 
    }
    
    /* Table itself */
    .custom-table { 
        width: 100%; 
        border-collapse: collapse;
        background: #FFFFFF;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Table header */
    .custom-table thead { 
        background: #FAFAFA;
        position: sticky;
        top: 0;
        z-index: 5;
    }
    
    .custom-table th { 
        padding: 10px 24px; 
        text-align: left; 
        font-weight: 500; 
        color: #9CA3AF; 
        font-size: 0.6875rem; 
        text-transform: uppercase;
        letter-spacing: 0.05em;
        
        background: #FAFAFA;
        white-space: nowrap;
        line-height: 1;
    }
    
    .custom-table th:first-child {
        padding-left: 24px;
    }
    
    .custom-table th:last-child {
        padding-right: 24px;
    }
    
    /* Table body */
    .custom-table tbody tr {
        
        transition: background-color 0.1s ease;
    }
    
    .custom-table tbody tr:hover {
        background-color: #F9FAFB;
    }
    
    .custom-table tbody tr:last-child {
        
    }
    
    .custom-table td { 
        padding: 16px 24px; 
        color: #374151; 
        font-size: 0.875rem;
        line-height: 1.25rem;
        vertical-align: middle;
        background: transparent;
    }
    
    .custom-table td:first-child {
        padding-left: 24px;
    }
    
    .custom-table td:last-child {
        padding-right: 24px;
    }
    
    /* Status dot - minimalist style */
    .status-dot {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.875rem;
        font-weight: 400;
        color: #374151;
    }
    
    .status-dot::before {
        content: '';
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
        display: block;
    }
    
    .status-dot.open::before { 
        background-color: #EF4444;
    }
    
    .status-dot.ready::before { 
        background-color: #10B981;
    }
    
    /* Table cell specific styles */
    .table-unit { 
        font-weight: 600; 
        color: #111827;
        font-size: 0.875rem;
    }
    
    .table-event { 
        color: #6B7280;
        font-size: 0.875rem;
        font-weight: 400;
    }
    
    .table-location {
        color: #6B7280;
        font-size: 0.875rem;
        font-weight: 400;
    }
    
    .table-value { 
        color: #111827; 
        font-weight: 500;
        font-size: 0.875rem;
    }
    
    .table-muted { 
        color: #9CA3AF;
        font-size: 0.875rem;
        font-weight: 400;
    }
    
    .status-dot.open::before { background: #EF4444; }
    .status-dot.open { color: #374151; }
    
    .status-dot.ready::before { background: #10B981; }
    .status-dot.ready { color: #374151; }
    
    .table-unit { font-weight: 600; color: #111827; }
    .table-event { color: #6B7280; }
    .table-value { color: #10B981; font-weight: 500; }
    .table-muted { color: #9CA3AF; }

    /* Duration text - Soft Red for Open status */
    .duration-red {
        color: #F87171 !important;
        font-weight: 600;
    }
    .table-value {
        color: #F87171 !important;
        font-weight: 600;
    }


    .duration-green {
        color: #10B981 !important;
        font-weight: 600;
    }


    /* Tertiary/minimal buttons - transparent, icon only */
    button[data-testid="stBaseButton-tertiary"],
    button[data-testid="stBaseButton-minimal"],
    .stButton > button[data-testid="stBaseButton-tertiary"],
    .stButton > button[data-testid="stBaseButton-minimal"] {
        background: transparent !important;
        background-color: transparent !important;
        
        color: #64748B !important;
    }

    /* Secondary buttons - light gray, NEVER black */
    button[data-testid="stBaseButton-secondary"],
    .stButton button[data-testid="stBaseButton-secondary"],
    div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"],
    [data-testid="column"] button[data-testid="stBaseButton-secondary"],
    [data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-secondary"] {
        background: #F1F5F9 !important;
        background-color: #F1F5F9 !important;
        color: #475569 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    }

    /* Remove ALL Streamlit default borders */
    .stSelectbox > div > div,
    .stDateInput > div > div,
    [data-baseweb="select"] > div,
    [data-baseweb="input"],
    [data-baseweb="base-input"],
    .stTextInput > div > div > input,
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stHorizontalBlock"],
    .stButton button {
        border: none !important;
        outline: none !important;
    }
    
    /* Override any inline borders */
    * {
        border-color: transparent !important;
    }
    
    /* But keep border-radius */
    .stSelectbox > div > div,
    .stDateInput > div > div,
    .stButton button {
        border-radius: 8px !important;
    }

</style>
""", unsafe_allow_html=True)

# Inject JavaScript for auto-refresh, scroll containment and live timer
# Using height=1 to ensure JavaScript executes properly
components.html("""
<div style="height:0;overflow:hidden;">
<script>
(function() {
    // AUTO-REFRESH - Smart reload yang preserve query params (page state)
    var autoRefreshInterval = 300000; // 300 seconds (5 minutes)
    
    function smartRefresh() {
        try {
            // Extract page param from current URL
            var urlParams = new URLSearchParams(window.parent.location.search);
            var currentPage = urlParams.get('page') || 'Overview';
            
            // Build new URL with preserved page param
            var baseUrl = window.parent.location.pathname;
            var newUrl = baseUrl + '?page=' + currentPage + '&t=' + Date.now();
            
            console.log('Auto-refresh to: ' + newUrl);
            window.parent.location.href = newUrl;
        } catch(e) {
            console.log('Auto-refresh error:', e);
            window.parent.location.reload();
        }
    }
    
    // Start auto-refresh timer
    console.log('Auto-refresh scheduled in 60 seconds');
    setTimeout(smartRefresh, autoRefreshInterval);
    
    // LIVE DURATION TIMER - updates every second
    function updateLiveDurations() {
        const doc = window.parent.document;
        const elements = doc.querySelectorAll('.live-duration');
        const now = new Date();
        elements.forEach(function(el) {
            const startStr = el.getAttribute('data-start');
            if (startStr) {
                const start = new Date(startStr);
                const diffMs = now - start;
                if (diffMs > 0) {
                    const totalMins = Math.floor(diffMs / (1000 * 60));
                    const hours = Math.floor(totalMins / 60);
                    const mins = totalMins % 60;
                    if (hours >= 24) {
                        const days = Math.floor(hours / 24);
                        const remHours = hours % 24;
                        el.textContent = days + 'd ' + remHours + 'h ' + mins + 'm';
                    } else {
                        el.textContent = hours + 'h ' + mins + 'm';
                    }
                }
            }
        });
    }
    setInterval(updateLiveDurations, 1000);
    setTimeout(updateLiveDurations, 500);
    
    // LIVE TOTAL DOWNTIME - updates every second
    function updateTotalDowntime() {
        const doc = window.parent.document;
        const el = doc.querySelector('.live-total-downtime');
        if (el) {
            const closedHours = parseFloat(el.getAttribute('data-closed-hours')) || 0;
            const openStartsStr = el.getAttribute('data-open-starts');
            let openHours = 0;
            
            if (openStartsStr) {
                try {
                    const openStarts = JSON.parse(openStartsStr);
                    const now = new Date();
                    openStarts.forEach(function(startStr) {
                        const start = new Date(startStr);
                        const diffMs = now - start;
                        if (diffMs > 0) {
                            openHours += diffMs / (1000 * 60 * 60);
                        }
                    });
                } catch(e) {
                    console.log('Error parsing open starts:', e);
                }
            }
            
            const totalHours = closedHours + openHours;
            el.textContent = totalHours.toFixed(1) + 'h';
        }
    }
    setInterval(updateTotalDowntime, 1000);
    setTimeout(updateTotalDowntime, 500);
    
    // SCROLL CONTAINMENT
    function setupScrollContainment() {
        const doc = window.parent.document;
        const lists = doc.querySelectorAll('.unit-list');
        lists.forEach(function(list) {
            if (!list.dataset.scrollSetup) {
                list.dataset.scrollSetup = 'true';
                list.addEventListener('wheel', function(e) {
                    const scrollTop = this.scrollTop;
                    const scrollHeight = this.scrollHeight;
                    const height = this.clientHeight;
                    const delta = e.deltaY;
                    
                    if (scrollHeight > height) {
                        if ((delta > 0 && scrollTop + height < scrollHeight) || 
                            (delta < 0 && scrollTop > 0)) {
                            e.preventDefault();
                            e.stopPropagation();
                            this.scrollTop += delta;
                        }
                    }
                }, {passive: false});
            }
        });
    }
    
    setTimeout(setupScrollContainment, 500);
    setInterval(setupScrollContainment, 2000);
})();
</script>
</div>
""", height=1)

PASTEL_COLORS = {
    'primary': '#3B82F6', 'secondary': '#64748B', 'success': '#10B981', 'danger': '#EF4444',
    'chart_colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
}

# SVG Icons with Colors
ICONS = {
    'location': '<svg viewBox="0 0 24 24" fill="#EF4444" style="width:14px;height:14px;"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>',
    'wrench': '<svg viewBox="0 0 24 24" fill="#F59E0B" style="width:14px;height:14px;"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
    'clock': '<svg viewBox="0 0 24 24" fill="#8B5CF6" style="width:14px;height:14px;"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>',
    'timer': '<svg viewBox="0 0 24 24" fill="#10B981" style="width:14px;height:14px;"><path d="M15 1H9v2h6V1zm-4 13h2V8h-2v6zm8.03-6.61l1.42-1.42c-.43-.51-.9-.99-1.41-1.41l-1.42 1.42C16.07 4.74 14.12 4 12 4c-4.97 0-9 4.03-9 9s4.02 9 9 9 9-4.03 9-9c0-2.12-.74-4.07-1.97-5.61zM12 20c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"/></svg>',
    'note': '<svg viewBox="0 0 24 24" fill="#6366F1" style="width:14px;height:14px;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>'
}

# ========================================
# GOOGLE SHEETS CONNECTION
# ========================================
@st.cache_resource(ttl=120)
def connect_to_gsheet():
    try:
        credentials_dict = dict(st.secrets["gcp_service_account"])
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key("1gxmFZLLNBarlMBrJZFpdvyMaihyNrbWUkxk8F2iRCN0")
        try:
            sheet = spreadsheet.worksheet("unit_breakdown_tracker")
        except:
            sheet = spreadsheet.get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        raise e

@st.cache_data(ttl=60, show_spinner=False)
def load_data():
    """Load data from Google Sheets with retry logic"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            sheet = connect_to_gsheet()
            all_values = sheet.get_all_values()
            if len(all_values) < 2:
                raise Exception("No data rows in sheet")
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            if not df.empty:
                df = df.dropna(how='all')
                
                if 'start_date' in df.columns and 'start_time' in df.columns:
                    df['start_datetime_str'] = df['start_date'].astype(str) + ' ' + df['start_time'].astype(str)
                    df['start_date'] = pd.to_datetime(df['start_datetime_str'], errors='coerce')
                elif 'start_date' in df.columns:
                    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
                
                if 'end_date' in df.columns and 'end_time' in df.columns:
                    mask = df['end_date'].astype(str).str.strip() != ''
                    df['end_datetime_str'] = ''
                    df.loc[mask, 'end_datetime_str'] = df.loc[mask, 'end_date'].astype(str) + ' ' + df.loc[mask, 'end_time'].astype(str)
                    df['end_date'] = pd.to_datetime(df['end_datetime_str'], errors='coerce')
                elif 'end_date' in df.columns:
                    df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
                
                for col in ['created_at', 'closed_at', 'last_modified']:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                
                if 'end_date' not in df.columns or df['end_date'].isna().all():
                    if 'closed_at' in df.columns:
                        df['end_date'] = df['closed_at']
                
                if 'total_duration_hours' in df.columns:
                    df['total_duration_hours'] = pd.to_numeric(df['total_duration_hours'], errors='coerce')
                if 'is_deleted' in df.columns:
                    df['is_deleted'] = pd.to_numeric(df['is_deleted'], errors='coerce').fillna(0)
                    df = df[df['is_deleted'] != 1]
            # Pre-calculate status to avoid recalculating on every page switch
            if not df.empty:
                def calc_status(row):
                    if 'status' in row.index and pd.notna(row['status']) and str(row['status']).strip():
                        status_val = str(row['status']).strip().capitalize()
                        if status_val in ['Ready', 'Closed']:
                            return 'Ready'
                        elif status_val == 'Open':
                            return 'Open'
                    if pd.isna(row.get('end_date')):
                        return 'Open'
                    return 'Ready'
                df['current_status'] = df.apply(calc_status, axis=1)
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                import time
                time.sleep(1)  # Wait 1 second before retry
                # Clear cache on retry
                st.cache_resource.clear()
                continue
            else:
                print(f"Failed to load data after {max_retries} attempts: {str(e)}")
                return pd.DataFrame()
    
    return pd.DataFrame()

def calculate_status(row):
    if 'status' in row.index and pd.notna(row['status']) and str(row['status']).strip():
        status_val = str(row['status']).strip().capitalize()
        if status_val in ['Ready', 'Closed']:
            return 'Ready'
        elif status_val == 'Open':
            return 'Open'
    if pd.isna(row.get('end_date')):
        return 'Open'
    now_aware = datetime.now(TIMEZONE)
    end_date = row['end_date']
    if end_date.tzinfo is None:
        end_date = TIMEZONE.localize(end_date)
    return 'Ready' if end_date <= now_aware else 'Open'

# ========================================
# UNIT ICON SYSTEM
# ========================================
def load_unit_icons_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'unit_icons.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {"unit_icons": {}, "fallback_emoji": "vehicle"}

def get_unit_icon_html(unit_code, size=68):
    config = load_unit_icons_config()
    code = str(unit_code).upper().strip()
    unit_icons = config.get('unit_icons', {})
    
    matched_type = None
    if code in unit_icons:
        matched_type = code
    else:
        best_match_len = 0
        for unit_type in unit_icons.keys():
            ut = unit_type.upper()
            if ut in code:
                if len(unit_type) > best_match_len:
                    best_match_len = len(unit_type)
                    matched_type = unit_type
    
    if matched_type:
        icon_info = unit_icons[matched_type]
        image_file = icon_info.get('image', '')
        image_path = os.path.join(os.path.dirname(__file__), 'image', image_file)
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/png;base64,{img_data}" style="width:{size}px;height:{size}px;object-fit:contain;">'
            except:
                pass
    return f'<div style="width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;font-size:2rem;color:#94A3B8;">&#128663;</div>'

def get_logo_base64():
    """Load and encode the optrack logo"""
    try:
        logo_path = os.path.join(os.path.dirname(__file__), 'image', 'optrack.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            return img_data
    except:
        pass
    return None

def get_metric_icon_base64(icon_name):
    """Load and encode a metric icon (Downtime.png, breakdown.png, ready.png)"""
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'image', icon_name)
        if os.path.exists(icon_path):
            with open(icon_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            return img_data
    except:
        pass
    return None

# ========================================
# UI COMPONENTS - REDESIGNED UNIT CARDS
# ========================================
def render_unit_cards(df, title="Units"):
    df = df.sort_values('start_date', ascending=False)
    if df.empty:
        st.markdown('<div class="empty-state">No units to display</div>', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="unit-list">', unsafe_allow_html=True)
    for _, row in df.iterrows():
        icon_html = get_unit_icon_html(row['unit_code'], 68)
        status_class = 'ready' if row['current_status'] == 'Ready' else 'open'
        start_str = row['start_date'].strftime('%d %b %H:%M') if pd.notna(row['start_date']) else '-'
        # Live duration for Open, static for Ready
        if row['current_status'] == 'Open' and pd.notna(row['start_date']):
            start_iso = row['start_date'].strftime('%Y-%m-%dT%H:%M:%S')
            duration = f'<span class="live-duration duration-red" data-start="{start_iso}">calculating...</span>'
        else:
            dur_val = f"{row['total_duration_hours']:.1f}h" if pd.notna(row['total_duration_hours']) else '0h'
            duration = f'<span class="duration-green">{dur_val}</span>'
        event_type = str(row['event_type'])[:30] + ('...' if len(str(row['event_type'])) > 30 else '')
        
        # Notes handling
        notes = str(row.get('noted', '')) if pd.notna(row.get('noted', '')) else ''
        notes_html = f'<div class="unit-notes">{notes}</div>' if notes.strip() else ''
        
        st.markdown(f"""
        <div class="unit-card">
            <div class="unit-img">{icon_html}</div>
            <div class="unit-content">
                <div class="unit-header">
                    <div class="unit-name">{row['unit_code']}</div>
                    <span class="status-badge {status_class}">{row['current_status']}</span>
                </div>
                <div class="unit-info-row">
                    <span class="info-item">
                        <span class="info-icon">{ICONS['location']}</span>
                        {row['pit']}
                    </span>
                    <span class="info-item">
                        <span class="info-icon">{ICONS['wrench']}</span>
                        {event_type}
                    </span>
                </div>
                <div class="unit-info-row">
                    <span class="info-item">
                        <span class="info-icon">{ICONS['timer']}</span>
                        {duration}
                    </span>
                    <span class="info-item">
                        <span class="info-icon">{ICONS['clock']}</span>
                        {start_str}
                    </span>
                </div>
                {notes_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_custom_table(df):
    if df.empty:
        st.info("No records to display")
        return
    
    display_df = df.copy()
    if 'end_date' not in display_df.columns or display_df['end_date'].isna().all():
        if 'closed_at' in display_df.columns:
            display_df['end_date'] = display_df['closed_at']
    
    # Table header
    table_html = '<table class="custom-table"><thead><tr>'
    table_html += '<th>Status</th><th>Unit</th><th>Event</th><th>Location</th><th>Start</th><th>End</th><th>Duration</th>'
    table_html += '</tr></thead><tbody>'
    
    # Table rows
    for _, row in display_df.sort_values('start_date', ascending=False).iterrows():
        unit = row.get('unit_code', '-')
        status = row.get('current_status', 'Open')
        event = str(row.get('event_type', '-'))
        pit = row.get('pit', '-')
        start = row['start_date'].strftime('%Y-%m-%d %H:%M') if pd.notna(row.get('start_date')) else '-'
        end = row['end_date'].strftime('%Y-%m-%d %H:%M') if pd.notna(row.get('end_date')) else '-'
        # Live duration for Open, static for Ready
        if status == 'Open' and pd.notna(row.get('start_date')):
            start_iso = row['start_date'].strftime('%Y-%m-%dT%H:%M:%S')
            hours = f'<span class="live-duration duration-red" data-start="{start_iso}">calculating...</span>'
        else:
            dur_val = f"{row['total_duration_hours']:.1f}h" if pd.notna(row.get('total_duration_hours')) else '0.0h'
            hours = f'<span class="duration-green">{dur_val}</span>'
        
        status_class = 'ready' if status == 'Ready' else 'open'
        status_text = 'Ready' if status == 'Ready' else 'Open'
        
        table_html += f'''<tr>
            <td><span class="status-dot {status_class}">{status_text}</span></td>
            <td class="table-unit">{unit}</td>
            <td class="table-event">{event}</td>
            <td class="table-location">{pit}</td>
            <td class="table-muted">{start}</td>
            <td class="table-muted">{end}</td>
            <td class="table-value">{hours}</td>
        </tr>'''
    
    table_html += '</tbody></table>'
    
    # Wrap in scroll container
    st.markdown(f'<div class="table-scroll-container">{table_html}</div>', unsafe_allow_html=True)

# ========================================
# MAIN APPLICATION
# ========================================
# Initialize session state BEFORE main function
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Overview'

def main():
    # Get query params to preserve page state across refreshes
    query_params = st.query_params
    
    # Initialize or restore current_page from query params
    if 'page' in query_params:
        st.session_state.current_page = query_params['page']
    elif 'current_page' not in st.session_state:
        st.session_state.current_page = 'Overview'
    
    # Update query params to match current page
    st.query_params['page'] = st.session_state.current_page
    
    # Safety check for session state
    current_page = st.session_state.get('current_page', 'Overview')
    
    # Load data (cached for 60 seconds, minimal blank time)
    df = load_data()
    if df.empty:
        st.error("No data available")
        if st.button("Retry"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
        return
    
    # Status already calculated in load_data() - cached
    
    # Header navigation
    nav_col1, nav_col2, nav_col3 = st.columns([1.5, 6, 2])
    with nav_col1:
        logo_b64 = get_logo_base64()
        if logo_b64:
            st.markdown(f'<div style="padding: 4px 0;"><img src="data:image/png;base64,{logo_b64}" style="height: 32px; object-fit: contain;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size: 1.1rem; font-weight: 700; padding: 8px 0; color: #1E293B;">OpTrack</div>', unsafe_allow_html=True)
    with nav_col2:
        btn_cols = st.columns([1, 1, 0.7, 5])
        with btn_cols[0]:
            if st.button("Overview", key="nav_overview", width='stretch', 
                        type="primary" if current_page == 'Overview' else "secondary"):
                st.session_state.current_page = 'Overview'
                st.query_params['page'] = 'Overview'
                st.rerun()
        with btn_cols[1]:
            if st.button("Analytics", key="nav_analytics", width='stretch',
                        type="primary" if current_page == 'Analytics' else "secondary"):
                st.session_state.current_page = 'Analytics'
                st.query_params['page'] = 'Analytics'
                st.rerun()
        with btn_cols[2]:
            # Refresh button - relies on global CSS for styling
            if st.button("⟳", key="nav_refresh", help="Sync Data", type="secondary", width='stretch'):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.rerun()
    with nav_col3:
        st.markdown(f'<div style="text-align:right; padding: 10px 0; color: #94A3B8; font-size: 0.8rem;">{datetime.now(TIMEZONE).strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    
    # Filters
    min_date = df['start_date'].min().date() if pd.notna(df['start_date'].min()) else datetime.now(TIMEZONE).date() - timedelta(days=30)
    max_date = datetime.now(TIMEZONE).date()
    f1, f2, f3, f4, f5, f6 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
    with f1:
        st.markdown('<div class="filter-label">Unit</div>', unsafe_allow_html=True)
        selected_unit = st.selectbox("Unit", ['All Units'] + sorted(df['unit_code'].unique().tolist()), label_visibility="collapsed", key="filter_unit")
    with f2:
        st.markdown('<div class="filter-label">Location</div>', unsafe_allow_html=True)
        selected_pit = st.selectbox("Location", ['All PIT'] + sorted(df['pit'].unique().tolist()), label_visibility="collapsed", key="filter_pit")
    with f3:
        st.markdown('<div class="filter-label">Status</div>', unsafe_allow_html=True)
        selected_status = st.selectbox("Status", ['All Status', 'Open', 'Ready'], label_visibility="collapsed", key="filter_status")
    with f4:
        st.markdown('<div class="filter-label">Event Type</div>', unsafe_allow_html=True)
        selected_event = st.selectbox("Event", ['All Events'] + sorted(df['event_type'].unique().tolist()), label_visibility="collapsed", key="filter_event")
    with f5:
        st.markdown('<div class="filter-label">Start Date</div>', unsafe_allow_html=True)
        start_date = st.date_input("Start", min_date, min_value=min_date, max_value=max_date, label_visibility="collapsed", key="filter_start_date")
    with f6:
        st.markdown('<div class="filter-label">End Date</div>', unsafe_allow_html=True)
        end_date = st.date_input("End", max_date, min_value=min_date, max_value=max_date, label_visibility="collapsed", key="filter_end_date")
    
    # Apply filters
    filtered_df = df.copy()
    if selected_unit != 'All Units':
        filtered_df = filtered_df[filtered_df['unit_code'] == selected_unit]
    if selected_pit != 'All PIT':
        filtered_df = filtered_df[filtered_df['pit'] == selected_pit]
    if selected_status != 'All Status':
        filtered_df = filtered_df[filtered_df['current_status'] == selected_status]
    if selected_event != 'All Events':
        filtered_df = filtered_df[filtered_df['event_type'] == selected_event]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['start_date'].dt.date >= start_date) & (filtered_df['start_date'].dt.date <= end_date)]
    
    # Metrics (for Analytics page)
    total = filtered_df['unit_code'].nunique()
    open_count = filtered_df[filtered_df['current_status'] == 'Open']['unit_code'].nunique()
    ready_count = filtered_df[filtered_df['current_status'] == 'Ready']['unit_code'].nunique()
    avg_dur = filtered_df['total_duration_hours'].mean()
    
    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
    
    # PAGE CONTENT
    if current_page == 'Overview':
        # Both sections use table view now
        col1, col2 = st.columns(2)
        open_df = filtered_df[filtered_df['current_status'] == 'Open']
        ready_df = filtered_df[filtered_df['current_status'] == 'Ready']
        with col1:
            st.markdown(f'<div class="section-header"><span class="section-indicator red"></span><span class="section-title">Current Breakdown</span><span class="section-count">{len(open_df)}</span></div>', unsafe_allow_html=True)
            render_breakdown_table(open_df, get_unit_icon_html)
        with col2:
            st.markdown(f'<div class="section-header"><span class="section-indicator green"></span><span class="section-title">Ready</span><span class="section-count">{len(ready_df)}</span></div>', unsafe_allow_html=True)
            render_ready_table(ready_df, get_unit_icon_html)
    else:
        # ANALYTICS PAGE - Clean Modern Design
        # Calculate total downtime: Ready units use total_duration_hours, Open units use live time
        open_df_analytics = filtered_df[filtered_df['current_status'] == 'Open']
        ready_df_analytics = filtered_df[filtered_df['current_status'] == 'Ready']
        
        # Static hours from closed/ready units
        closed_hours = ready_df_analytics['total_duration_hours'].sum() if not ready_df_analytics.empty else 0
        
        # Calculate live hours from open units (current snapshot - will be updated by JS)
        open_hours = 0
        open_start_times = []  # Store start times for JS live calculation
        for _, row in open_df_analytics.iterrows():
            if pd.notna(row.get('start_date')):
                start_dt = row['start_date']
                if start_dt.tzinfo is None:
                    start_dt = TIMEZONE.localize(start_dt)
                now = datetime.now(TIMEZONE)
                diff = (now - start_dt).total_seconds() / 3600  # hours
                open_hours += max(0, diff)
                open_start_times.append(start_dt.strftime('%Y-%m-%dT%H:%M:%S'))
        
        total_hours = closed_hours + open_hours
        open_count = len(open_df_analytics)
        ready_count = len(ready_df_analytics)
        
        # JSON encode start times for JavaScript
        import json as json_module
        open_starts_json = json_module.dumps(open_start_times)
        
        # Get icon base64 data
        downtime_icon = get_metric_icon_base64('Downtime.png')
        breakdown_icon = get_metric_icon_base64('breakdown.png')
        ready_icon = get_metric_icon_base64('ready.png')
        
        # Metric Cards Row
        m1, m2, m3 = st.columns(3)
        with m1:
            icon_html = f'<img src="data:image/png;base64,{downtime_icon}" style="width:48px;height:48px;object-fit:contain;">' if downtime_icon else ''
            st.markdown(f'''
            <div style="background: #FFFFFF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div class="live-total-downtime" data-closed-hours="{closed_hours}" data-open-starts='{open_starts_json}' style="font-size: 1.5rem; font-weight: 700; color: #111827;">{total_hours:.1f}h</div>
                    <div style="color: #6B7280; font-size: 0.75rem; margin-top: 4px;">Total Downtime</div>
                </div>
                {icon_html}
            </div>
            ''', unsafe_allow_html=True)
        with m2:
            icon_html = f'<img src="data:image/png;base64,{breakdown_icon}" style="width:48px;height:48px;object-fit:contain;">' if breakdown_icon else ''
            st.markdown(f'''
            <div style="background: #FFFFFF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #111827;">{open_count}</div>
                    <div style="color: #6B7280; font-size: 0.75rem; margin-top: 4px;">Open Breakdowns</div>
                </div>
                {icon_html}
            </div>
            ''', unsafe_allow_html=True)
        with m3:
            icon_html = f'<img src="data:image/png;base64,{ready_icon}" style="width:48px;height:48px;object-fit:contain;">' if ready_icon else ''
            st.markdown(f'''
            <div style="background: #FFFFFF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06); display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #111827;">{ready_count}</div>
                    <div style="color: #6B7280; font-size: 0.75rem; margin-top: 4px;">Ready Units</div>
                </div>
                {icon_html}
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        
        # Charts Row - 3 columns
        c1, c2, c3 = st.columns(3)
        
        with c1:
            recent = filtered_df[filtered_df['start_date'] >= (datetime.now(TIMEZONE).replace(tzinfo=None)) - timedelta(days=14)]
            if not recent.empty:
                daily = recent.groupby(recent['start_date'].dt.date).size().reset_index(name='count')
                fig = go.Figure(go.Bar(
                    x=pd.to_datetime(daily['start_date']), 
                    y=daily['count'], 
                    marker=dict(color='#8B5CF6'),
                    text=daily['count'],
                    textposition='outside',
                    textfont=dict(size=11, color='#374151'),
                    cliponaxis=False
                ))
                fig.update_layout(
                    title=dict(text='14-Day Trend', font=dict(size=14, color='#111827', family='Inter'), x=0, y=0.95),
                    height=320,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FFFFFF',
                    margin=dict(t=40, b=40, l=40, r=20),
                    xaxis=dict(showgrid=False, tickfont=dict(color='#9CA3AF', size=10)),
                    yaxis=dict(showgrid=True, gridcolor='#F3F4F6', tickfont=dict(color='#9CA3AF', size=10), zeroline=False)
                )
                st.plotly_chart(fig, width='stretch', config={'displayModeBar': False}, key="trend")
        
        with c2:
            events = filtered_df['event_type'].value_counts().head(5)
            if not events.empty:
                colors = []
                for event in events.index:
                    if 'unschedule' in str(event).lower():
                        colors.append('#F97316')  # Orange
                    elif 'schedule' in str(event).lower():
                        colors.append('#60A5FA')  # Blue
                    else:
                        colors.append('#8B5CF6')  # Purple
                fig2 = go.Figure(go.Bar(
                    y=events.index, 
                    x=events.values, 
                    orientation='h', 
                    marker=dict(color=colors),
                    text=events.values,
                    textposition='outside',
                    textfont=dict(size=11, color='#374151'),
                    cliponaxis=False
                ))
                fig2.update_layout(
                    title=dict(text='Events by Type', font=dict(size=14, color='#111827', family='Inter'), x=0, y=0.95),
                    height=320,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FFFFFF',
                    margin=dict(t=40, b=40, l=20, r=40),
                    xaxis=dict(showgrid=True, gridcolor='#F3F4F6', tickfont=dict(color='#9CA3AF', size=10)),
                    yaxis=dict(showgrid=False, tickfont=dict(color='#6B7280', size=10))
                )
                st.plotly_chart(fig2, width='stretch', config={'displayModeBar': False}, key="events")
        
        with c3:
            status_counts = filtered_df['current_status'].value_counts()
            if not status_counts.empty:
                colors = ['#60A5FA', '#34D399'] if 'Open' in status_counts.index else ['#34D399', '#60A5FA']
                if len(status_counts) == 1:
                    colors = ['#60A5FA'] if status_counts.index[0] == 'Open' else ['#34D399']
                fig3 = go.Figure(data=[go.Pie(
                    labels=status_counts.index,
                    values=status_counts.values,
                    hole=0.6,
                    marker=dict(colors=colors, line=dict(color='#FFFFFF', width=3)),
                    textinfo='percent',
                    textposition='outside',
                    textfont=dict(size=12, color='#374151')
                )])
                fig3.update_layout(
                    height=320,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FFFFFF',
                    margin=dict(t=50, b=40, l=20, r=80),
                    title=dict(text='Status Distribution', font=dict(size=14, color='#111827'), x=0, y=0.98),
                    showlegend=True,
                    legend=dict(
                        orientation="v", 
                        yanchor="middle",
                        y=0.5, 
                        xanchor="left",
                        x=1.02,
                        font=dict(color='#374151', size=11)
                    )
                )
                st.plotly_chart(fig3, width='stretch', config={'displayModeBar': False}, key="status")
        
        st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
        
        # Table Section with proper header layout
        st.markdown('<div style="background: #FFFFFF; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06); overflow: hidden;">', unsafe_allow_html=True)
        
        # Header row: Title left, CSV button right
        hdr_col1, hdr_col2 = st.columns([6, 1])
        with hdr_col1:
            st.markdown('<p style="font-size: 1rem; font-weight: 600; color: #111827; margin: 12px 0 12px 20px;">All Records</p>', unsafe_allow_html=True)
        with hdr_col2:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 CSV", 
                data=csv_data,
                file_name=f"breakdown_{datetime.now(TIMEZONE).strftime('%Y%m%d')}.csv", 
                mime="text/csv",
                key="download_csv",
                width='stretch'
            )
        st.markdown('<div style="height: 1px; background: #E5E7EB;"></div>', unsafe_allow_html=True)
        
        # Table content
        render_custom_table(filtered_df)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()