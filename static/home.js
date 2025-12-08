// home.js

let currentDate = new Date();
let currentView = 'month'; // Default to Month
let events = JSON.parse(localStorage.getItem('gaonEvents')) || [];
let schoolEvents = []; // From API

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

    // Modal Logic
    const modal = document.getElementById('eventModal');
    const closeBtn = document.querySelector('.close-modal');
    const cancelBtn = document.querySelector('.cancel-btn');
    const eventForm = document.getElementById('eventForm');
    const addEventBtn = document.getElementById('addEventBtn');

    if(closeBtn) closeBtn.onclick = () => closeModal();
    if(cancelBtn) cancelBtn.onclick = () => closeModal();
    window.onclick = (event) => {
        if (event.target == modal) closeModal();
    };

    if(addEventBtn) {
        addEventBtn.addEventListener('click', () => {
            const today = new Date();
            const y = today.getFullYear();
            const m = String(today.getMonth() + 1).padStart(2, '0');
            const d = String(today.getDate()).padStart(2, '0');
            openModal(`${y}-${m}-${d}`);
        });
    }

    if(eventForm) {
        eventForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveEvent();
        });
    }

    // Initial Fetch & Render
    fetchSchoolEvents();
    render();
    loadWidgets();
});

function loadWidgets() {
    // Legacy removed or empty
}

async function fetchSchoolEvents() {
    const y = currentDate.getFullYear();
    const m = String(currentDate.getMonth() + 1).padStart(2, '0'); // 01-12
    const monthParam = `${y}-${m}`;

    try {
        // Proxy to Real Backend
        const res = await fetch(`/school/event?month=${monthParam}`);
        if(res.ok) {
            const data = await res.json();
            if(data.items) {
                // Map API events to local structure
                // API: { title, startDate(YYYYMMDD), endDate, description }
                schoolEvents = data.items.map(item => {
                    const dStr = item.startDate; // YYYYMMDD
                    const dateFmt = `${dStr.substring(0,4)}-${dStr.substring(4,6)}-${dStr.substring(6,8)}`;
                    return {
                        id: 'school_' + dStr + item.title,
                        title: item.title,
                        date: dateFmt,
                        time: '09', // All day essentially
                        color: '#e74c3c', // School events in Red/Distinct color
                        type: 'school'
                    };
                });
            }
        }
    } catch (e) {
        console.error("Failed to fetch school events:", e);
    }
    render(); // Re-render with new data
}

function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view-switch button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`${view}ViewBtn`).classList.add('active');
    render();
}

function navigate(direction) {
    if (currentView === 'day') {
        currentDate.setDate(currentDate.getDate() + direction);
    } else if (currentView === 'week') {
        currentDate.setDate(currentDate.getDate() + (direction * 7));
    } else if (currentView === 'month') {
        currentDate.setMonth(currentDate.getMonth() + direction);
        fetchSchoolEvents(); // Fetch new month data
    } else if (currentView === 'year') {
        currentDate.setFullYear(currentDate.getFullYear() + direction);
    }
    render();
}

function goToToday() {
    currentDate = new Date();
    if(currentView === 'month') fetchSchoolEvents();
    render();
}

// --- Event Logic ---

function openModal(dateStr, time = "09") {
    const modal = document.getElementById('eventModal');
    if(!modal) return;
    document.getElementById('eventDate').value = dateStr;
    document.getElementById('eventTime').value = time;
    document.getElementById('eventTitle').value = '';
    
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('eventModal');
    if(modal) modal.style.display = 'none';
}

function saveEvent() {
    const title = document.getElementById('eventTitle').value;
    const date = document.getElementById('eventDate').value; // YYYY-MM-DD
    const time = document.getElementById('eventTime').value; // HH
    const color = document.getElementById('eventColor').value;

    if (!title || !date) return;

    const newEvent = {
        id: Date.now(),
        title,
        date,
        time,
        color,
        type: 'personal'
    };

    events.push(newEvent);
    localStorage.setItem('gaonEvents', JSON.stringify(events));
    
    closeModal();
    render();
}

function getAllEvents() {
    return [...events, ...schoolEvents];
}

function getEventsForDateAndTime(dateObj, hourStr) {
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    const dateStr = `${y}-${m}-${d}`;
    
    const all = getAllEvents();
    return all.filter(e => e.date === dateStr && parseInt(e.time) === parseInt(hourStr));
}

function getEventsForDate(dateObj) {
     const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    const dateStr = `${y}-${m}-${d}`;

    const all = getAllEvents();
    return all.filter(e => e.date === dateStr);
}

// --- Render Functions ---

function render() {
    const dayHeaders = document.getElementById('dayHeaders'); 
    const calendarGrid = document.getElementById('calendarGrid'); 
    const timezoneContainer = document.querySelector('.timezone-info'); 
    
    // Update Header Text
    const monthDisplay = document.getElementById('currentMonthDisplay');
    if(monthDisplay) {
        monthDisplay.textContent = currentDate.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' });
    }

    if(dayHeaders) dayHeaders.innerHTML = '';
    if(calendarGrid) calendarGrid.innerHTML = '';
    if(timezoneContainer) timezoneContainer.classList.remove('week-grid-layout', 'day-grid-layout');
    
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


function renderWeek(container, headerEl, gridEl) {
    if(container) {
        container.style.display = 'block'; 
        container.classList.add('week-grid-layout');
    }
    
    const startDate = new Date(currentDate);
    startDate.setDate(currentDate.getDate() - currentDate.getDay());

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

    for (let i = 7; i <= 15; i++) { 
        const timeLabel = i > 12 ? `${i-12} PM` : (i === 12 ? '12 PM' : `${i} AM`);
        const rowDiv = document.createElement('div');
        rowDiv.className = 'time-row';

        let rowHTML = `<div class="time-label">${timeLabel}</div>`;
        rowDiv.innerHTML = rowHTML;
        
        for(let j=0; j<7; j++) {
            const cellDate = new Date(startDate);
            cellDate.setDate(startDate.getDate() + j);
            const isTodayCol = isSameDate(cellDate, today);
            
            const cell = document.createElement('div');
            cell.className = `day-cell ${isTodayCol ? 'current-day-col' : ''}`;
            
            // Render Events
            const cellEvents = getEventsForDateAndTime(cellDate, i);
            cellEvents.forEach(evt => {
                const evtDiv = document.createElement('div');
                evtDiv.className = 'event-item';
                evtDiv.textContent = evt.title;
                evtDiv.style.backgroundColor = evt.color;
                cell.appendChild(evtDiv);
            });

            cell.addEventListener('click', (e) => {
                if(e.target === cell) { 
                    const y = cellDate.getFullYear();
                    const m = String(cellDate.getMonth() + 1).padStart(2, '0');
                    const d = String(cellDate.getDate()).padStart(2, '0');
                    openModal(`${y}-${m}-${d}`, i);
                }
            });

            rowDiv.appendChild(cell);
        }
        
        const spacer = document.createElement('div');
        spacer.className = 'day-cell';
        rowDiv.appendChild(spacer);

        gridEl.appendChild(rowDiv);
    }
}

function renderDay(container, headerEl, gridEl) {
    if(container) {
        container.style.display = 'block';
        container.classList.add('day-grid-layout');
    }

    const today = new Date();
    const isToday = isSameDate(currentDate, today);

    let headerHTML = `<div class="time-col-header"></div>`;
    headerHTML += `
        <div class="day-col ${isToday ? 'current-day' : ''}" style="border-right:1px solid #eee;">
            <span class="day-name">${currentDate.toLocaleDateString('en-US', { weekday: 'long' }).toUpperCase()}</span>
            <span class="day-num">${currentDate.getDate()}</span>
        </div>
    `;
    headerHTML += `<div class="info-col"></div>`;
    headerEl.innerHTML = headerHTML;

    for (let i = 7; i <= 15; i++) {
        const timeLabel = i > 12 ? `${i-12} PM` : (i === 12 ? '12 PM' : `${i} AM`);
        
        const rowDiv = document.createElement('div');
        rowDiv.className = 'time-row';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'time-label';
        labelDiv.textContent = timeLabel;
        rowDiv.appendChild(labelDiv);

        const cell = document.createElement('div');
        cell.className = `day-cell ${isToday ? 'current-day-col' : ''}`;
        
        const cellEvents = getEventsForDateAndTime(currentDate, i);
        cellEvents.forEach(evt => {
            const evtDiv = document.createElement('div');
            evtDiv.className = 'event-item';
            evtDiv.textContent = evt.title;
            evtDiv.style.backgroundColor = evt.color;
            cell.appendChild(evtDiv);
        });

        cell.addEventListener('click', (e) => {
            if(e.target === cell) {
                 const y = currentDate.getFullYear();
                const m = String(currentDate.getMonth() + 1).padStart(2, '0');
                const d = String(currentDate.getDate()).padStart(2, '0');
                openModal(`${y}-${m}-${d}`, i);
            }
        });

        rowDiv.appendChild(cell);
        
        const spacer = document.createElement('div');
        spacer.className = 'day-cell';
        rowDiv.appendChild(spacer);

        gridEl.appendChild(rowDiv);
    }
}

function renderMonth(gridEl) {
    const timezoneContainer = document.querySelector('.timezone-info');
    if(timezoneContainer) timezoneContainer.style.display = 'none';

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(firstDay.getDate() - firstDay.getDay());

    const container = document.createElement('div');
    container.className = 'month-container';
    
    const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
    days.forEach(d => {
        const dDiv = document.createElement('div');
        dDiv.className = 'month-header-cell';
        dDiv.textContent = d;
        container.appendChild(dDiv);
    });

    const tempDate = new Date(startDate);
    const today = new Date();

    for (let i = 0; i < 42; i++) {
        const isToday = isSameDate(tempDate, today);
        const isOtherMonth = tempDate.getMonth() !== month;
        
        const cell = document.createElement('div');
        cell.className = `month-day-cell ${isOtherMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}`;
        
        const dateNum = document.createElement('span');
        dateNum.className = 'date-num';
        dateNum.textContent = tempDate.getDate();
        cell.appendChild(dateNum);

        // Render Events (dots/text)
        const cellEvents = getEventsForDate(tempDate);
        cellEvents.forEach(evt => {
            const evtDiv = document.createElement('div');
            evtDiv.className = 'event-item';
            evtDiv.textContent = evt.title; // In month view just text
            evtDiv.style.backgroundColor = evt.color;
            cell.appendChild(evtDiv);
        });
        
        const y = tempDate.getFullYear();
        const m = String(tempDate.getMonth() + 1).padStart(2, '0');
        const d = String(tempDate.getDate()).padStart(2, '0');
        
        cell.addEventListener('click', (e) => {
            if(e.target === cell || e.target === dateNum) {
                openModal(`${y}-${m}-${d}`, 9);
            }
        });

        container.appendChild(cell);
        tempDate.setDate(tempDate.getDate() + 1);
    }
    
    gridEl.appendChild(container);
}

function renderYear(gridEl) {
    const timezoneContainer = document.querySelector('.timezone-info');
    if(timezoneContainer) timezoneContainer.style.display = 'none';
    
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


