/* ==========================================================================
   Nimbus Weather Application — Main JavaScript Logic & Dynamic Themes
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // --- State Management ---
    let currentWeatherData = null;
    let currentUnit = 'C'; // Default unit
    const RECENT_KEY = 'nimbus_recent_searches';

    // --- DOM Elements ---
    const searchForm = document.getElementById('search-form');
    const cityInput = document.getElementById('city-input');
    const geoBtn = document.getElementById('geo-btn');

    const unitCelsiusBtn = document.getElementById('unit-celsius');
    const unitFahrenheitBtn = document.getElementById('unit-fahrenheit');

    const errorBanner = document.getElementById('error-banner');
    const errorMessage = document.getElementById('error-message');
    const loadingSpinner = document.getElementById('loading-spinner');
    const dashboardGrid = document.getElementById('weather-dashboard');

    const recentSearchesContainer = document.getElementById('recent-searches');
    const recentTagsContainer = document.getElementById('recent-tags');

    // Dashboard DOM Nodes
    const cityNameEl = document.getElementById('city-name');
    const countryNameEl = document.getElementById('country-name');
    const currentTempEl = document.getElementById('current-temp');
    const weatherConditionEl = document.getElementById('weather-condition');
    const weatherIconContainer = document.getElementById('weather-icon-container');

    const feelsLikeEl = document.getElementById('feels-like');
    const humidityEl = document.getElementById('humidity');
    const windSpeedEl = document.getElementById('wind-speed');
    const pressureEl = document.getElementById('pressure');

    const hourlyContainer = document.getElementById('hourly-container');
    const dailyContainer = document.getElementById('daily-container');

    // Weather Condition Feather Icon Mapping
    const ICON_MAP = {
        'clear-day': 'sun',
        'partly-cloudy-day': 'cloud-sun',
        'cloudy': 'cloud',
        'fog': 'cloud-off',
        'drizzle': 'cloud-drizzle',
        'rain': 'cloud-rain',
        'heavy-rain': 'cloud-rain',
        'snow': 'cloud-snow',
        'showers': 'cloud-rain',
        'thunderstorm': 'cloud-lightning',
        'unknown': 'sun'
    };

    // --- Initial Setup ---
    initApp();

    function initApp() {
        renderRecentSearches();
        // Load default initial city on startup
        fetchWeatherByCity('London');
    }

    // --- API Fetching Methods ---
    async function fetchWeatherByCity(city) {
        if (!city.trim()) return;

        showLoading();
        hideError();

        try {
            const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch weather data.');
            }

            currentWeatherData = data;
            renderDashboard(data);
            saveRecentSearch(data.location.name);

        } catch (err) {
            showError(err.message);
        } finally {
            hideLoading();
        }
    }

    async function fetchWeatherByCoords(lat, lon) {
        showLoading();
        hideError();

        try {
            const response = await fetch(`/api/weather/coords?lat=${lat}&lon=${lon}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch location weather.');
            }

            currentWeatherData = data;
            renderDashboard(data);

        } catch (err) {
            showError(err.message);
        } finally {
            hideLoading();
        }
    }

    // --- DOM Rendering Engine ---
    function renderDashboard(data) {
        // Update ambient weather theme
        updateTheme(data);

        // Location Info
        cityNameEl.textContent = data.location.name;
        countryNameEl.textContent = data.location.country ? data.location.country : 'Current Location';

        // Temperatures & Conditions
        currentTempEl.textContent = formatTemp(data.current.temperature);
        weatherConditionEl.textContent = data.current.condition;
        
        // Update Primary Icon
        const iconName = ICON_MAP[data.current.icon] || 'sun';
        weatherIconContainer.innerHTML = `<i data-feather="${iconName}"></i>`;

        // Key Atmospheric Metrics
        feelsLikeEl.textContent = `${formatTemp(data.current.feels_like)}°${currentUnit}`;
        humidityEl.textContent = `${data.current.humidity}%`;
        windSpeedEl.textContent = `${data.current.wind_speed} km/h`;
        pressureEl.textContent = `${data.current.pressure} hPa`;

        // Render Hourly Forecast Slider
        renderHourly(data.hourly);

        // Render Daily Forecast Grid
        renderDaily(data.daily);

        // Replace Feather SVG Icons across newly generated HTML
        if (window.feather) {
            feather.replace();
        }
    }

    function renderHourly(hourlyList) {
        hourlyContainer.innerHTML = '';
        hourlyList.forEach(item => {
            const timeFormatted = new Date(item.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const iconName = ICON_MAP[item.icon] || 'cloud';

            const hourlyEl = document.createElement('div');
            hourlyEl.className = 'hourly-item';
            hourlyEl.innerHTML = `
                <span class="hourly-time">${timeFormatted}</span>
                <i data-feather="${iconName}"></i>
                <span class="hourly-temp">${formatTemp(item.temp)}°${currentUnit}</span>
                <span class="hourly-precip" style="font-size:0.75rem; color: var(--accent-blue);">${item.precip_probability}%</span>
            `;
            hourlyContainer.appendChild(hourlyEl);
        });
    }

    function renderDaily(dailyList) {
        dailyContainer.innerHTML = '';
        dailyList.forEach(item => {
            const dateObj = new Date(item.date);
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
            const iconName = ICON_MAP[item.icon] || 'cloud';

            const dailyEl = document.createElement('div');
            dailyEl.className = 'daily-item';
            dailyEl.innerHTML = `
                <span class="daily-date">${dayName}</span>
                <div style="display:flex; align-items:center; gap:8px;">
                    <i data-feather="${iconName}"></i>
                    <span style="font-size:0.9rem; color: var(--text-secondary);">${item.condition}</span>
                </div>
                <span class="daily-precip" style="font-size:0.85rem; color: var(--accent-blue);">${item.precip_probability}% Rain</span>
                <span class="daily-temps">${formatTemp(item.temp_max)}° / ${formatTemp(item.temp_min)}°${currentUnit}</span>
            `;
            dailyContainer.appendChild(dailyEl);
        });
    }

    // --- Dynamic Weather Theme Controller ---
    function updateTheme(data) {
        document.body.classList.remove('theme-clear', 'theme-clouds', 'theme-rain', 'theme-snow', 'theme-night');

        if (data.current.is_day === 0) {
            document.body.classList.add('theme-night');
            return;
        }

        const icon = data.current.icon;
        if (icon.includes('clear')) {
            document.body.classList.add('theme-clear');
        } else if (icon.includes('cloud')) {
            document.body.classList.add('theme-clouds');
        } else if (icon.includes('rain') || icon.includes('drizzle') || icon.includes('showers')) {
            document.body.classList.add('theme-rain');
        } else if (icon.includes('snow')) {
            document.body.classList.add('theme-snow');
        }
    }

    // --- Temperature Unit Conversion Utility ---
    function formatTemp(tempInCelsius) {
        if (currentUnit === 'F') {
            return Math.round((tempInCelsius * 9/5) + 32);
        }
        return Math.round(tempInCelsius);
    }

    function switchUnit(newUnit) {
        if (currentUnit === newUnit) return;
        currentUnit = newUnit;

        unitCelsiusBtn.classList.toggle('active', currentUnit === 'C');
        unitFahrenheitBtn.classList.toggle('active', currentUnit === 'F');

        // Re-render DOM with stored weather data without hitting backend API
        if (currentWeatherData) {
            renderDashboard(currentWeatherData);
        }
    }

    // --- Browser Geolocation Handling ---
    function getUserLocation() {
        if (!navigator.geolocation) {
            showError("Geolocation is not supported by your browser.");
            return;
        }

        showLoading();
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                fetchWeatherByCoords(latitude, longitude);
            },
            (error) => {
                hideLoading();
                showError("Location permission denied. Please enter a city manually.");
            }
        );
    }

    // --- Recent Searches (localStorage) ---
    function saveRecentSearch(cityName) {
        if (!cityName) return;
        let searches = JSON.parse(localStorage.getItem(RECENT_KEY)) || [];
        
        // Remove duplicates and append new city to front
        searches = searches.filter(c => c.toLowerCase() !== cityName.toLowerCase());
        searches.unshift(cityName);
        
        // Retain top 5 searches
        if (searches.length > 5) searches.pop();

        localStorage.setItem(RECENT_KEY, JSON.stringify(searches));
        renderRecentSearches();
    }

    function renderRecentSearches() {
        const searches = JSON.parse(localStorage.getItem(RECENT_KEY)) || [];
        if (searches.length === 0) {
            recentSearchesContainer.classList.add('hidden');
            return;
        }

        recentSearchesContainer.classList.remove('hidden');
        recentTagsContainer.innerHTML = '';

        searches.forEach(city => {
            const tag = document.createElement('span');
            tag.className = 'recent-tag';
            tag.textContent = city;
            tag.addEventListener('click', () => fetchWeatherByCity(city));
            recentTagsContainer.appendChild(tag);
        });
    }

    // --- State Indicators ---
    function showLoading() {
        loadingSpinner.classList.remove('hidden');
        dashboardGrid.style.opacity = '0.4';
    }

    function hideLoading() {
        loadingSpinner.classList.add('hidden');
        dashboardGrid.style.opacity = '1';
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorBanner.classList.remove('hidden');
        if (window.feather) feather.replace();
    }

    function hideError() {
        errorBanner.classList.add('hidden');
    }

    // --- Event Listeners ---
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = cityInput.value.trim();
        if (city) {
            fetchWeatherByCity(city);
            cityInput.value = '';
        }
    });

    geoBtn.addEventListener('click', getUserLocation);

    unitCelsiusBtn.addEventListener('click', () => switchUnit('C'));
    unitFahrenheitBtn.addEventListener('click', () => switchUnit('F'));
});