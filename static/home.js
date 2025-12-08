// home.js

let currentDate = new Date();
let currentView = 'week'; // 'day', 'week', 'month', 'year'
let events = JSON.parse(localStorage.getItem('gaonEvents')) || [];

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

    closeBtn.onclick = () => closeModal();
    cancelBtn.onclick = () => closeModal();
    window.onclick = (event) => {
        if (event.target == modal) closeModal();
    };

    addEventBtn.addEventListener('click', () => {
        const today = new Date();
        const y = today.getFullYear();
        const m = String(today.getMonth() + 1).padStart(2, '0');
        const d = String(today.getDate()).padStart(2, '0');
        openModal(`${y}-${m}-${d}`);
    });

    eventForm.addEventListener('submit', (e) => {
        e.preventDefault();
        saveEvent();
    });

    render();
    loadWidgets();
});

function loadWidgets() {
    // Mock Data for Lunch
    const lunchMenu = [
        "Main: Spicy Pork Bulgogi",
        "Soup: Soybean Paste Soup",
        "Side: Kimchi, Seasoned Spinach",
        "Dessert: Fruit Salad"
    ];
    
    // Mock Data for Timetable (e.g., today's classes)
    const timeTable = [
        { period: 1, subject: "Mathematics" },
        { period: 2, subject: "English" },
        { period: 3, subject: "History" },
        { period: 4, subject: "Science" },
        { period: 5, subject: "Physical Ed" }
    ];

    // Inject Lunch
    const lunchContainer = document.querySelector('.lunch-widget .widget-content');
    if (lunchContainer) {
        let html = '<ul style="list-style: none; padding: 0;">';
        lunchMenu.forEach(item => {
            html += `<li style="margin-bottom: 5px; padding-left: 10px; border-left: 2px solid #3498db;">${item}</li>`;
        });
        html += '</ul>';
        lunchContainer.innerHTML = html;
    }

    // Inject Timetable
    const timeContainer = document.querySelector('.timetable-widget .widget-content');
    if (timeContainer) {
        let html = '<ul style="list-style: none; padding: 0;">';
        timeTable.forEach(cls => {
            html += `<li style="margin-bottom: 8px; display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 4px;">
                <span style="font-weight: 500; color: #333;">${cls.period}교시</span>
                <span>${cls.subject}</span>
            </li>`;
        });
        html += '</ul>';
        timeContainer.innerHTML = html;
    }
}

function switchView(view) {
    currentView = view;
    
    // Update active button state
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
    } else if (currentView === 'year') {
        currentDate.setFullYear(currentDate.getFullYear() + direction);
    }
    render();
}

function goToToday() {
    currentDate = new Date();
    render();
}

// --- Event Logic ---

function openModal(dateStr, time = "09") {
    const modal = document.getElementById('eventModal');
    document.getElementById('eventDate').value = dateStr;
    document.getElementById('eventTime').value = time;
    document.getElementById('eventTitle').value = '';
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('eventModal').style.display = 'none';
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
        color
    };

    events.push(newEvent);
    localStorage.setItem('gaonEvents', JSON.stringify(events));
    
    closeModal();
    render();
}

function getEventsForDateAndTime(dateObj, hourStr) {
    // Helper to format date as YYYY-MM-DD
    const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    const dateStr = `${y}-${m}-${d}`;

    return events.filter(e => e.date === dateStr && parseInt(e.time) === parseInt(hourStr));
}

function getEventsForDate(dateObj) {
     const y = dateObj.getFullYear();
    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
    const d = String(dateObj.getDate()).padStart(2, '0');
    const dateStr = `${y}-${m}-${d}`;

    return events.filter(e => e.date === dateStr);
}

// --- Render Functions ---

function render() {
    const dayHeaders = document.getElementById('dayHeaders'); 
    const calendarGrid = document.getElementById('calendarGrid'); 
    const timezoneContainer = document.querySelector('.timezone-info'); 
    
    dayHeaders.innerHTML = '';
    calendarGrid.innerHTML = '';
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


function renderWeek(container, headerEl, gridEl) {
    container.style.display = 'block'; 
    container.classList.add('week-grid-layout');
    
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

            // Add Click Listener to Open Modal
            cell.addEventListener('click', (e) => {
                if(e.target === cell) { // Only if clicking cell, not event
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
    container.style.display = 'block';
    container.classList.add('day-grid-layout');

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
        
        // Render Events
        const cellEvents = getEventsForDateAndTime(currentDate, i);
        cellEvents.forEach(evt => {
            const evtDiv = document.createElement('div');
            evtDiv.className = 'event-item';
            evtDiv.textContent = evt.title;
            evtDiv.style.backgroundColor = evt.color;
            cell.appendChild(evtDiv);
        });

        // Add Click Listener
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
    document.querySelector('.timezone-info').style.display = 'none';

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
        
        // Month view click to add event (defaulting to 9am)
        // Need to capture date value correctly as tempDate changes
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


// Append fetch logic to home.js
document.addEventListener('DOMContentLoaded', () => {
    // Fetch Timetable (Request only)
    fetch('/api/timetable')
        .catch(err => console.log('Timetable request sent.'));
});

