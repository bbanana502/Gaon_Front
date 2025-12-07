// home.js

let currentDate = new Date();
let currentView = 'week'; // 'day', 'week', 'month', 'year'

document.addEventListener('DOMContentLoaded', () => {
    // Navigation Buttons
    document.getElementById('prevWeekBtn').addEventListener('click', () => navigate(-1));
    document.getElementById('nextWeekBtn').addEventListener('click', () => navigate(1));
    document.getElementById('todayBtn').addEventListener('click', goToToday);

    // View Switcher
    document.getElementById('dayViewBtn').addEventListener('click', () => switchView('day'));
    document.getElementById('weekViewBtn').addEventListener('click', () => switchView('week'));
    document.getElementById('monthViewBtn').addEventListener('click', () => switchView('month'));
    document.getElementById('yearViewBtn').addEventListener('click', () => switchView('year'));

    render();
});

function switchView(view) {
    currentView = view;
    
    // Update active button state
    document.querySelectorAll('.view-switch button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`${view}ViewBtn`).classList.add('active');

    // Reset grid layout classes
    const container = document.getElementById('calendarGrid').parentElement; // timezone-info container
    // We might need to restructure HTML slightly or just swap content completely
    
    render();
}

function navigate(direction) {
    if (currentView === 'day') {
        currentDate.setDate(currentDate.getDate() + direction);
    } else if (currentView === 'week') {
        currentDate.setDate(currentDate.getDate() + (direction * 7));
    } else if (currentView === 'month') {
        currentDate.setMonth(currentDate.getMonth() + direction);
    } else if (currentView === 'year') {
        currentDate.setFullYear(currentDate.getFullYear() + direction);
    }
    render();
}

function goToToday() {
    currentDate = new Date();
    render();
}

function render() {
    const dayHeaders = document.getElementById('dayHeaders'); // For Day/Week headers
    const calendarGrid = document.getElementById('calendarGrid'); // For Main Content
    
    const timezoneContainer = document.querySelector('.timezone-info'); 
    
    // Clear previous view content
    dayHeaders.innerHTML = '';
    calendarGrid.innerHTML = '';
    
    // Remove specific layout classes
    timezoneContainer.classList.remove('week-grid-layout', 'day-grid-layout');
    
    if (currentView === 'week') {
        renderWeek(timezoneContainer, dayHeaders, calendarGrid);
    } else if (currentView === 'day') {
        renderDay(timezoneContainer, dayHeaders, calendarGrid);
    } else if (currentView === 'month') {
        renderMonth(calendarGrid);
    } else if (currentView === 'year') {
        renderYear(calendarGrid);
    }
}

// --- Render Functions ---

function renderWeek(container, headerEl, gridEl) {
    container.style.display = 'block'; // Ensure headers are visible
    container.classList.add('week-grid-layout');
    
    // Calculate start of week (Sunday)
    const startDate = new Date(currentDate);
    startDate.setDate(currentDate.getDate() - currentDate.getDay());

    // Generate Headers
    let headerHTML = `<div class="time-col-header"></div>`;
    const tempDate = new Date(startDate);
    const today = new Date();

    for (let i = 0; i < 7; i++) {
        const isToday = isSameDate(tempDate, today);
        headerHTML += `
            <div class="day-col ${isToday ? 'current-day' : ''}">
                <span class="day-name">${tempDate.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()}</span>
                <span class="day-num">${tempDate.getDate()}</span>
            </div>
        `;
        tempDate.setDate(tempDate.getDate() + 1);
    }
    headerHTML += `<div class="info-col"><span class="tz-label">EST</span><span class="tz-offset">GMT-5</span></div>`;
    headerEl.innerHTML = headerHTML;

    // Generate Grid Rows (Static Times for now)
    for (let i = 7; i <= 15; i++) { // 7 AM to 3 PM
        const timeLabel = i > 12 ? `${i-12} PM` : (i === 12 ? '12 PM' : `${i} AM`);
        let rowHTML = `<div class="time-row"><div class="time-label">${timeLabel}</div>`;
        
        // Cells
        for(let j=0; j<7; j++) {
            // Highlight today column
            const cellDate = new Date(startDate);
            cellDate.setDate(startDate.getDate() + j);
            const isTodayCol = isSameDate(cellDate, today);
            
            rowHTML += `<div class="day-cell ${isTodayCol ? 'current-day-col' : ''}"></div>`;
        }
        
        rowHTML += `<div class="day-cell"></div></div>`; // Info col spacer
        gridEl.innerHTML += rowHTML;
    }
}

function renderDay(container, headerEl, gridEl) {
    container.style.display = 'block';
    container.classList.add('day-grid-layout');

    const today = new Date();
    const isToday = isSameDate(currentDate, today);

    // Header
    let headerHTML = `<div class="time-col-header"></div>`;
    headerHTML += `
        <div class="day-col ${isToday ? 'current-day' : ''}" style="border-right:1px solid #eee;">
            <span class="day-name">${currentDate.toLocaleDateString('en-US', { weekday: 'long' }).toUpperCase()}</span>
            <span class="day-num">${currentDate.getDate()}</span>
        </div>
    `;
    headerHTML += `<div class="info-col"></div>`;
    headerEl.innerHTML = headerHTML;

    // Grid
    for (let i = 7; i <= 15; i++) {
        const timeLabel = i > 12 ? `${i-12} PM` : (i === 12 ? '12 PM' : `${i} AM`);
        gridEl.innerHTML += `
            <div class="time-row">
                <div class="time-label">${timeLabel}</div>
                <div class="day-cell ${isToday ? 'current-day-col' : ''}"></div>
                <div class="day-cell"></div>
            </div>
        `;
    }
}

function renderMonth(gridEl) {
    // Hide standard headers container, we build our own structure
    document.querySelector('.timezone-info').style.display = 'none';

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // First day of the month
    const firstDay = new Date(year, month, 1);
    // Start date for grid (go back to Sunday)
    const startDate = new Date(firstDay);
    startDate.setDate(firstDay.getDate() - firstDay.getDay());

    let html = `<div class="month-container">`;
    
    // Headers (Sun..Sat)
    const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
    days.forEach(d => html += `<div class="month-header-cell">${d}</div>`);

    // 6 weeks to cover all months
    const tempDate = new Date(startDate);
    const today = new Date();

    for (let i = 0; i < 42; i++) {
        const isToday = isSameDate(tempDate, today);
        const isOtherMonth = tempDate.getMonth() !== month;
        
        html += `
            <div class="month-day-cell ${isOtherMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}">
                <span class="date-num">${tempDate.getDate()}</span>
            </div>
        `;
        tempDate.setDate(tempDate.getDate() + 1);
    }
    
    html += `</div>`;
    gridEl.innerHTML = html;
}

function renderYear(gridEl) {
    document.querySelector('.timezone-info').style.display = 'none';
    
    const year = currentDate.getFullYear();
    let html = `<div class="year-container">`;
    
    for (let m = 0; m < 12; m++) {
        const monthDate = new Date(year, m, 1);
        const monthName = monthDate.toLocaleDateString('en-US', { month: 'long' });
        
        html += `
            <div class="year-month-card">
                <div class="year-month-title">${monthName}</div>
                <div class="mini-month-grid">
        `;
        
        // Mini grid logic
        const start = new Date(year, m, 1);
        start.setDate(start.getDate() - start.getDay());
        
        for(let d=0; d<42; d++) {
             html += `<div class="mini-day">${start.getDate()}</div>`;
             start.setDate(start.getDate() + 1);
        }
        
        html += `</div></div>`;
    }
    
    html += `</div>`;
    gridEl.innerHTML = html;
}

function isSameDate(d1, d2) {
    return d1.getDate() === d2.getDate() && 
           d1.getMonth() === d2.getMonth() && 
           d1.getFullYear() === d2.getFullYear();
}
