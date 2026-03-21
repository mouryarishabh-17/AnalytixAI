// ============================================
// CONFIGURATION
// ============================================
const API_BASE_URL = "http://127.0.0.1:8000";

// Global state
let currentDomain = '';
let currentSessionId = null;
let currentReportId = null; // Mongo ID for report download
let currentFile = null;
let authMode = 'login';
let allHistory = []; // Local cache for history records
let isGuestMode = true; // Guest Mode Flag

// ============================================
// TAB NAVIGATION SYSTEM
// ============================================
function switchTab(tabName) {
    // Guest Mode: Allow browsing all tabs. Login required only for specific actions (like selecting data).

    console.log(`Switching to tab: ${tabName}`);

    // Sync active tab in sidebar and top nav
    document.querySelectorAll('.nav-item, .top-nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-tab') === tabName) {
            item.classList.add('active');
        }
    });

    // Update tab content visibility
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'datasources': 'Data Sources',
        'analytics': 'Analytics',
        'chat': 'AI Chat',
        'settings': 'Profile & Settings'
    };
    document.getElementById('page-title').textContent = titles[tabName] || tabName;

    // Sync theme toggle if entering settings
    if (tabName === 'settings') {
        setTimeout(updateThemeToggleState, 100);
    }

    // Update URL hash
    history.pushState({ tab: tabName }, '', `#${tabName}`);
}

// ============================================
// SIDEBAR TOGGLE (Mobile)
// ============================================
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('active');
}

// ============================================
// THEME TOGGLE
// ============================================
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Update icon
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// ============================================
// AUTHENTICATION
// ============================================
function openAuth(mode) {
    authMode = mode;
    const modal = document.getElementById('auth-modal');
    const title = document.getElementById('auth-modal-title');
    const nameGroup = document.getElementById('name-group');
    const submitBtn = document.getElementById('auth-submit-btn');
    const switchText = document.getElementById('auth-switch-text');
    const switchBtn = document.getElementById('auth-switch-btn');

    if (mode === 'login') {
        title.textContent = 'Login';
        nameGroup.style.display = 'none';
        submitBtn.textContent = 'Login';
        switchText.textContent = "Don't have an account?";
        switchBtn.textContent = 'Register';
    } else {
        title.textContent = 'Register';
        nameGroup.style.display = 'block';
        submitBtn.textContent = 'Register';
        switchText.textContent = 'Already have an account?';
        switchBtn.textContent = 'Login';
    }

    modal.classList.add('active');

    // Clear previous inputs
    document.getElementById('auth-email').value = '';
    document.getElementById('auth-password').value = '';
    if (document.getElementById('auth-name')) document.getElementById('auth-name').value = '';

    const form = document.getElementById('auth-form');
    form.onsubmit = (e) => {
        e.preventDefault();
        if (authMode === 'login') {
            handleLogin();
        } else {
            handleRegister();
        }
    };
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('active');
}

function toggleAuthMode() {
    openAuth(authMode === 'login' ? 'register' : 'login');
}

// ============================================
// PAYMENT & PRO UPGRADE
// ============================================
function openPaymentModal() {
    document.getElementById('payment-modal').classList.add('active');
}

function closePaymentModal() {
    document.getElementById('payment-modal').classList.remove('active');
}

async function handlePaymentSubmit(event) {
    event.preventDefault();
    const btn = document.getElementById('pay-btn');
    const token = localStorage.getItem('access_token');

    if (!token) {
        showToast("Please login first to upgrade.", 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

    try {
        const response = await fetch(`${API_BASE_URL}/auth/upgrade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ amount: 49.00, payment_method: "Simulated Card" })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('user_plan', 'pro');
            updateUIForLoggedInUser();
            closePaymentModal();
            showToast('🌟 Congratulations! You are now a PRO member.', 'success');
            switchTab('analytics');
        } else {
            showToast('Upgrade failed: ' + (data.detail || 'Payment error'), 'error');
        }
    } catch (error) {
        console.error('Upgrade error:', error);
        showToast('Connection error during payment.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-lock"></i> Pay & Activate Pro';
    }
}

// ============================================
// LAYOUT TOGGLE
// ============================================
function toggleLayout() {
    const isTopNav = document.body.classList.toggle('layout-top-nav');
    localStorage.setItem('layout-mode', isTopNav ? 'top' : 'sidebar');

    // Sync active state
    const activeTab = document.querySelector('.nav-item.active')?.getAttribute('data-tab') || 'datasources';
    updateTopNavActiveState(activeTab);
}

function updateTopNavActiveState(tabName) {
    document.querySelectorAll('.top-nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-tab') === tabName) {
            item.classList.add('active');
        }
    });
}

async function handleLogin() {
    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user_email', email);
            localStorage.setItem('user_name', data.user_name || email.split('@')[0]);
            localStorage.setItem('user_bio', data.user_bio || "");
            localStorage.setItem('user_plan', data.user_plan || "free");
            localStorage.setItem('is_admin', data.is_admin || false);

            updateUIForLoggedInUser();
            closeAuthModal();
            showToast('Login successful!', 'success');
        } else {
            showToast((data.detail || data.message || 'Login failed'), 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Connection error. Check console for details.', 'error');
    }
}

async function handleRegister() {
    const name = document.getElementById('auth-name').value;
    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            openAuth('login');
        } else {
            const data = await response.json();
            showToast((data.error || data.detail || 'Registration failed'), 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showToast('Connection error. Please try again.', 'error');
    }
}

function updateUIForLoggedInUser() {
    // CRITICAL FIX: Ensure app knows we are NOT in guest mode
    isGuestMode = false;

    const name = localStorage.getItem('user_name') || "User";
    const email = localStorage.getItem('user_email') || "";
    const bio = localStorage.getItem('user_bio') || "";
    const plan = localStorage.getItem('user_plan') || "free";

    // Header buttons
    document.getElementById('auth-btn-login').style.display = 'none';
    document.getElementById('auth-btn-register').style.display = 'none';

    // Sidebar footer & Plan badge
    document.getElementById('sidebar-user-name').textContent = name;
    const roleEl = document.getElementById('sidebar-user-role');
    if (plan === 'pro') {
        roleEl.innerHTML = '<i class="fas fa-crown" style="color: #ffd700;"></i> Pro Account';
        roleEl.style.color = 'var(--primary)';
        if (document.getElementById('premium-upgrade-card')) {
            document.getElementById('premium-upgrade-card').style.display = 'none';
        }
    } else {
        // HIDE "Free Account" LABEL FOR REGULAR USERS AS REQUESTED
        roleEl.textContent = '';
        roleEl.style.display = 'none'; // Completely hide the element
        if (document.getElementById('premium-upgrade-card')) {
            document.getElementById('premium-upgrade-card').style.display = 'block';
        }
    }

    // Settings Tab (Profile Info)
    if (document.getElementById('settings-name')) {
        document.getElementById('settings-name').textContent = name;
        document.getElementById('settings-email').textContent = email;
        document.getElementById('input-name').value = name;
        document.getElementById('input-email').value = email;
        document.getElementById('input-bio').value = bio;
    }

    // Load History
    if (typeof loadHistory === 'function') {
        loadHistory();
    }

    // Check Admin Status
    const adminLink = document.getElementById('nav-item-admin');
    if (adminLink) {
        if (localStorage.getItem('is_admin') === 'true') {
            adminLink.style.display = 'flex';
        } else {
            adminLink.style.display = 'none';
        }
    }
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        showToast('Logged out successfully', 'info');
        setTimeout(() => {
            window.location.href = window.location.pathname;
        }, 800);
    }
}

// ============================================
// PROFILE MANAGEMENT
// ============================================
async function saveProfile() {
    const token = localStorage.getItem('access_token');
    const name = document.getElementById('input-name').value;
    const bio = document.getElementById('input-bio').value;

    if (!token) return showToast('Please login first', 'warning');

    const btn = document.querySelector('.form-actions .btn');
    const originalText = btn.textContent;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/update-profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name, bio, phone: "" })
        });

        if (response.ok) {
            localStorage.setItem('user_name', name);
            localStorage.setItem('user_bio', bio);
            updateUIForLoggedInUser();
            showToast('Profile updated successfully!', 'success');
        } else if (response.status === 401) {
            showToast('Session expired. Please login again.', 'error');
            handleLogout();
        } else {
            showToast('Failed to update profile', 'error');
        }
    } catch (error) {
        console.error('Update profile error:', error);
        showToast('Connection error', 'error');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// ============================================
// DATA SOURCES & ANALYSIS
// ============================================
function selectDomain(domain) {
    if (!checkAuth('domain')) return; // Require login for selection

    if (currentDomain !== domain) {
        cancelUpload(); // Clear previous file if switching domains
    }
    currentDomain = domain;
    switchTab('datasources');
    document.getElementById('domain-selection-card').style.display = 'none';
    document.getElementById('upload-card').style.display = 'block';

    // Update title precisely
    const displayDomain = domain.charAt(0).toUpperCase() + domain.slice(1);
    document.getElementById('upload-card-title').textContent = `Upload ${displayDomain} Data`;
}

function backToDomainSelection() {
    document.getElementById('domain-selection-card').style.display = 'grid';
    document.getElementById('upload-card').style.display = 'none';
    currentDomain = '';
}

// Domain Selection Reset (Sidebar Navigation)
function resetDomainSelection() {
    // 1. Switch to Data Sources content
    switchTab('datasources');

    // 2. Force View to Domain Selection Cards
    const domainCard = document.getElementById('domain-selection-card');
    const uploadCard = document.getElementById('upload-card');

    if (domainCard) domainCard.style.display = 'grid'; // Grid layout for cards
    if (uploadCard) uploadCard.style.display = 'none';

    // 3. Highlight Correct Sidebar Item
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const domainsNavItem = document.querySelector('.nav-item[onclick*="resetDomainSelection"]');
    if (domainsNavItem) domainsNavItem.classList.add('active');
}

function handleFileSelect(event, droppedFile = null) {
    const file = droppedFile || event.target.files[0];
    if (!file) return;
    currentFile = file;

    const preview = document.getElementById('file-preview');
    preview.style.display = 'block';
    preview.innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius);">
            <i class="fas fa-file-excel" style="font-size: 2rem; color: var(--success);"></i>
            <div>
                <div style="font-weight: 600;">${file.name}</div>
                <div style="font-size: 0.875rem; color: var(--text-muted);">${(file.size / (1024 * 1024)).toFixed(2)} MB</div>
            </div>
            <button class="btn-text" onclick="cancelUpload()" style="margin-left: auto;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    document.getElementById('upload-actions').style.display = 'flex';
}

function cancelUpload() {
    currentFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-preview').style.display = 'none';
    document.getElementById('upload-actions').style.display = 'none';
}



async function analyzeData(customMapping = null) {
    if (!currentFile || !currentDomain) return showToast('Select file and domain', 'warning');
    const token = localStorage.getItem('access_token');
    if (!token) return openAuth('login');

    const btn = document.getElementById('analyze-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

    // Check if customMapping is a valid object (not an event)
    let mappingToSend = null;
    if (customMapping && !(customMapping instanceof Event) && typeof customMapping === 'object') {
        mappingToSend = customMapping;
    }

    try {
        const formData = new FormData();
        formData.append('domain', currentDomain);
        formData.append('file', currentFile);

        if (mappingToSend) {
            formData.append('mapping', JSON.stringify(mappingToSend));
        }

        showLoadingDashboard();
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        const data = await response.json();

        // CHECK FOR MAPPING REQUIREMENT
        if (data.status === 'mapping_needed') {
            openMappingModal(data);
            return; // Stop here, wait for user mapping
        }

        if (response.ok) {
            // Store session ID for chat
            currentSessionId = data.session_id;

            displayResults(data);
            switchTab('analytics');

            // Automatically get data overview for chat
            if (currentSessionId) {
                await getDataOverview(currentSessionId);
            }
        } else if (response.status === 401) {
            alert('🔒 Your session has expired. Please login again.');
            handleLogout(); // Force logout to clear invalid token
        } else {
            alert('❌ ' + (data.detail || 'Upload failed'));
        }
    } catch (error) {
        console.error(error);
        alert('❌ Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-chart-bar"></i> Analyze Data';
        loadHistory(); // Refresh history after upload
    }
}


// ============================================
// HISTORY MANAGEMENT
// ============================================
async function loadHistory() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const container = document.getElementById('history-list-container');
    if (!container) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/history`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();

        if (response.ok && data.history) {
            allHistory = data.history;
            renderHistoryTable(data.history);
        } else if (response.status === 401) {
            console.warn('Session expired (401) during history load');
            handleLogout();
        }
    } catch (error) {
        console.error('Fetch history error:', error);
    }
}

function renderHistoryTable(history) {
    const container = document.getElementById('history-list-container');
    if (!history || history.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="padding: 3rem 1rem; text-align: center;">
                <i class="fas fa-folder-open" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 1rem; display: block;"></i>
                <p style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">No history yet</p>
                <p class="text-muted" style="margin-bottom: 1.5rem;">Start by choosing a data type above</p>
                <button class="btn btn-primary" onclick="resetDomainSelection()">
                    <i class="fas fa-plus"></i> Choose a Data Type
                </button>
            </div>
        `;
        return;
    }

    let html = `
        <div class="table-responsive">
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
    `;

    history.forEach(item => {
        const date = new Date(item.created_at).toLocaleString();
        html += `
            <tr>
                <td><i class="fas fa-file-csv"></i> ${item.filename}</td>
                <td><span class="badge-domain">${item.domain}</span></td>
                <td>${item.file_size_mb} MB</td>
                <td>${date}</td>
                <td>
                    <button class="btn-view" onclick="viewHistoryItem('${item._id}')">
                        View Analysis
                    </button>
                    <button class="btn-delete" onclick="deleteHistoryItem('${item._id}')" title="Delete" style="margin-left:5px; padding:6px 12px; background:#ef4444; color:white; border:none; border-radius:4px; cursor:pointer;">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    html += `</tbody></table></div>`;
    container.innerHTML = html;
}

function viewHistoryItem(id) {
    const item = allHistory.find(h => h._id === id);
    if (!item) return;

    displayResults(item);
    switchTab('analytics');
}

function displayResults(data) {
    const container = document.getElementById('results-container');
    container.innerHTML = ''; // Clear previous results

    // Add Global Actions Header (Fixed Button)
    const actionsHeader = document.createElement('div');
    actionsHeader.className = "dashboard-actions";
    actionsHeader.style.cssText = `
        position: fixed; 
        bottom: 30px; 
        right: 30px; 
        z-index: 2000;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
    `;
    actionsHeader.innerHTML = `
        <button class="btn btn-primary" onclick="downloadCustomReport()" style="padding: 12px 24px; font-size: 1rem; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); border-radius: 50px; font-weight: 600;">
            <i class="fas fa-file-pdf" style="margin-right: 8px;"></i> PDF Report
        </button>
    `;
    container.appendChild(actionsHeader);

    const analytics = data.analytics || {};
    const ml = analytics.ml_insights || {};

    // 1. ML Predictive Analysis Card (PRO FEATURE)
    if (data.analytics && data.analytics.ml_insights) {
        const ml = data.analytics.ml_insights;
        const isLocked = ml.status === 'locked';
        const isDataIssue = ml.status === 'data_issue' || ml.status === 'error';

        const mlCard = document.createElement('div');
        mlCard.className = `card border-glow ${isLocked ? 'ml-locked' : ''}`;

        if (isLocked) {
            mlCard.innerHTML = `
                <div class="card-header">
                    <h3><i class="fas fa-brain"></i> ML Predictive Analysis</h3>
                    <span class="badge" style="background: linear-gradient(90deg, #FDB931 0%, #F9A01B 100%); color: #000; font-weight: 700; padding: 5px 12px; border-radius: 50px; box-shadow: 0 2px 10px rgba(249, 160, 27, 0.3); font-size: 0.75rem; letter-spacing: 0.5px;">PRO FEATURE</span>
                </div>
                <div class="card-body">
                    <div class="ml-locked-bg"></div>
                    <div class="ml-locked-content">
                        <i class="fas fa-lock" style="font-size: 3.5rem; margin-bottom: 1.5rem; color: #F9A01B;"></i>
                        <h4 style="font-size: 1.5rem; margin-bottom: 1rem;">Unlock Advanced AI Insights</h4>
                        <p style="color: var(--text-secondary); max-width: 400px; margin: 0 auto; line-height: 1.6;">
                            Reveal hidden patterns, forecast trends, and identify key drivers in your data with our advanced machine learning models.
                        </p>
                        <button class="btn btn-primary" style="margin-top: 2rem; padding: 0.8rem 2.5rem; font-size: 1rem; background: linear-gradient(90deg, #FDB931 0%, #F9A01B 100%); color: #000; font-weight: 700; border: none; box-shadow: 0 4px 15px rgba(249, 160, 27, 0.4);" onclick="switchTab('settings')">
                            Upgrade to Pro
                        </button>
                    </div>
                </div>
            `;
        } else if (isDataIssue) {
            mlCard.innerHTML = `
                <div class="card-header">
                    <h3><i class="fas fa-brain"></i> ML Predictive Analysis</h3>
                    <span class="badge" style="background: var(--bg-secondary); color: var(--text-muted); border: 1px solid var(--border);">ANALYSIS SKIPPED</span>
                </div>
                <div class="card-body">
                    <div style="text-align: center; padding: 2.5rem 1rem;">
                        <div style="width: 70px; height: 70px; background: var(--bg-secondary); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem;">
                            <i class="fas fa-chart-bar" style="font-size: 2rem; color: var(--text-muted); opacity: 0.5;"></i>
                        </div>
                        <h4 style="font-size: 1.25rem; margin-bottom: 1rem; color: var(--text-primary);">Data Not Sufficient for Prediction</h4>
                        
                        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 8px; display: inline-block; max-width: 500px; text-align: left;">
                            <strong style="color: #ef4444; display: block; margin-bottom: 0.5rem;"><i class="fas fa-exclamation-circle"></i> Reason:</strong>
                            <p style="color: var(--text-primary); margin: 0; font-size: 0.95rem;">${ml.message}</p>
                        </div>

                        <div style="margin-top: 2rem; border-top: 1px solid var(--border); padding-top: 1.5rem; max-width: 500px; margin-left: auto; margin-right: auto;">
                            <p style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600; margin-bottom: 0.5rem;">WHAT WE NEED FOR ML:</p>
                            <ul style="text-align: left; font-size: 0.85rem; color: var(--text-secondary); list-style: none; padding: 0;">
                                <li style="margin-bottom: 5px;"><i class="fas fa-check" style="color: var(--success); margin-right: 8px;"></i> At least 15-20 rows of data</li>
                                <li style="margin-bottom: 5px;"><i class="fas fa-check" style="color: var(--success); margin-right: 8px;"></i> A relevant target column (e.g., 'Sales', 'Profit')</li>
                                <li><i class="fas fa-check" style="color: var(--success); margin-right: 8px;"></i> Diverse data values (not just a single repeated value)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        } else {
            mlCard.innerHTML = `
                <div class="card-header">
                    <h3><i class="fas fa-brain"></i> ML Predictive Analysis</h3>
                    <span class="badge-success">PRO ACTIVE</span>
                </div>
                <div class="card-body">
                    <div class="ml-summary-box">
                        <div class="ml-summary">${ml.summary || 'Patterns detected successfully.'}</div>
                        <div style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.5rem;">
                            Algorithm: ${ml.algorithm || 'Random Forest'} | Confidence: ${ml.accuracy || 'High'}
                        </div>
                    </div>
                    <h4 style="margin-bottom: 1rem; font-size: 0.875rem; text-transform: uppercase; color: var(--text-muted);">Predictive Factors (Weight)</h4>
                    <div class="drivers-grid">
                        ${(ml.top_drivers || []).map(d => `
                            <div class="driver-item">
                                <span class="driver-label">${d.feature}</span>
                                <div class="progress-bar"><div class="progress-fill" style="width: ${d.importance}%"></div></div>
                                <span class="driver-score">${d.importance}% impact</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        container.appendChild(mlCard);
    }

    const gridContainer = document.createElement('div');
    gridContainer.className = 'results-grid';
    let gridHtml = '';

    // 2. KEY OBSERVATIONS (FIELD WORK)
    if (analytics.key_insights && analytics.key_insights.length > 0) {
        gridHtml += `
            <div class="card">
                <div class="card-header"><h3><i class="fas fa-lightbulb"></i> Key Observations</h3></div>
                <div class="card-body">
                    <ul class="insight-list">
                        ${analytics.key_insights.map(ins => `
                            <li>
                                <strong>${ins.title}:</strong> ${ins.observation}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // 3. SUMMARY STATS (AGE, STRESS, ETC)
    if (analytics.summary_stats) {
        gridHtml += `
            <div class="card">
                <div class="card-header"><h3><i class="fas fa-chart-line"></i> Statistical Summary</h3></div>
                <div class="card-body">
                    ${Object.entries(analytics.summary_stats).map(([key, value]) => {
            const label = key.replace(/_/g, ' ').toUpperCase();

            if (typeof value === 'object' && value !== null) {
                return `
                                <div class="stat-group mt-md">
                                    <strong style="font-size: 0.8rem; color: var(--text-muted);">${label}</strong>
                                    <div class="tag-cloud mt-sm">
                                        ${Object.entries(value).map(([subK, subV]) => `
                                            <span class="tag">${subK}: ${subV}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            `;
            } else {
                return `
                                <div class="stat-item-row">
                                    <span>${label}:</span>
                                    <span class="badge-domain">${value}</span>
                                </div>
                                <div class="divider"></div>
                            `;
            }
        }).join('')}
                </div>
            </div>
        `;
    }

    // 4. CHARTS GRID
    if (data.charts && Object.keys(data.charts).length > 0) {
        // Update report ID for download
        currentReportId = data.report_id || data._id;

        gridHtml += `
            <div class="card full-width-card">
                <div class="card-header"><h3><i class="fas fa-images"></i> Visual Analysis</h3></div>
                <div class="card-body">
                    <div class="charts-grid-field">
                        ${Object.entries(data.charts).map(([name, url]) => `
                            <div class="field-chart-item" data-chart-name="${name}" style="position: relative; min-height: 300px; display: flex; flex-direction: column;">
                                <div class="chart-header-row">
                                    <h4>${name.replace(/_/g, ' ').toUpperCase()}</h4>
                                    ${!name.toLowerCase().includes('heatmap') && !name.toLowerCase().includes('scatter') ? `
                                    <div class="chart-controls">
                                        <button class="chart-btn" onclick="toggleChartDropdown(this)" title="Change Chart Type">
                                            <i class="fas fa-cog"></i>
                                        </button>
                                        <div class="chart-dropdown">
                                            <button class="chart-dropdown-item" onclick="switchChartType('${name}', 'bar', this)">
                                                <i class="fas fa-chart-bar"></i> Bar Chart
                                            </button>
                                            <button class="chart-dropdown-item" onclick="switchChartType('${name}', 'pie', this)">
                                                <i class="fas fa-chart-pie"></i> Pie Chart
                                            </button>
                                            <button class="chart-dropdown-item" onclick="switchChartType('${name}', 'line', this)">
                                                <i class="fas fa-chart-line"></i> Line Chart
                                            </button>
                                        </div>
                                    </div>
                                    ` : ''}
                                </div>
                                
                                <div class="chart-loader" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(255,255,255,0.02); border-radius: 8px; margin-top: 10px; min-height: 200px;">
                                    <i class="fas fa-circle-notch fa-spin" style="font-size: 2.5rem; color: var(--primary);"></i>
                                    <p class="text-muted" style="margin-top: 10px; font-size: 0.9rem;">Loading Visual...</p>
                                </div>

                                <img src="${API_BASE_URL}${url}?t=${new Date().getTime()}" 
                                     class="img-fluid rounded shadow-sm" 
                                     style="display: none; animation: fadeIn 0.8s;"
                                     onload="this.style.display='block'; this.previousElementSibling.style.display='none';">
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    gridContainer.innerHTML = gridHtml;
    container.appendChild(gridContainer);
}

// ============================================
// DRAG & DROP
// ============================================
function initDragAndDrop() {
    const uploadArea = document.getElementById('upload-area');
    if (!uploadArea) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragging'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragging'), false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFileSelect(null, files[0]);
    }
}

// ============================================
// INITIALIZATION
// ============================================
function updateThemeToggleState() {
    const theme = localStorage.getItem('theme') || 'light';
    const toggle = document.getElementById('theme-switch');
    if (toggle) toggle.checked = (theme === 'dark');
}

document.addEventListener('DOMContentLoaded', () => {
    // Auth & Theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    if (localStorage.getItem('access_token')) {
        updateUIForLoggedInUser();
    }

    // Apply Layout Preference
    if (localStorage.getItem('layout-mode') === 'top') {
        document.body.classList.add('layout-top-nav');
    }

    // Default Tab
    const hash = window.location.hash.slice(1);
    switchTab(hash && ['dashboard', 'datasources', 'analytics', 'chat', 'settings'].includes(hash) ? hash : 'datasources');

    // Drag & Drop
    initDragAndDrop();

    // Charts
    initDashboardCharts();
});

// ============================================
// CHART CONTROLS logic (Global Scope)
// ============================================
function toggleChartDropdown(btn) {
    const dropdown = btn.nextElementSibling;
    // Close other dropdowns
    document.querySelectorAll('.chart-dropdown.active').forEach(d => {
        if (d !== dropdown) d.classList.remove('active');
    });
    dropdown.classList.toggle('active');

    // Auto-close on click outside
    const closeMenu = (e) => {
        if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
            document.removeEventListener('click', closeMenu);
        }
    };
    if (dropdown.classList.contains('active')) {
        document.addEventListener('click', closeMenu);
    }
}

async function switchChartType(chartName, chartType, btn) {
    const card = btn.closest('.field-chart-item');
    const img = card.querySelector('img');
    const loader = card.querySelector('.chart-loader');
    const dropdown = btn.closest('.chart-dropdown');

    // Close menu
    if (dropdown) dropdown.classList.remove('active');

    // UI Loading State
    img.style.display = 'none';
    loader.style.display = 'flex';
    loader.innerHTML = `
        <i class="fas fa-circle-notch fa-spin" style="font-size: 2.5rem; color: var(--primary);"></i>
        <p class="text-muted" style="margin-top: 10px; font-size: 0.9rem;">Switching...</p>
    `;

    // Construct New URL (Local Switch)
    // Assumes backend has pre-generated: basename_pie.png, basename_line.png
    let currentSrc = img.src.split('?')[0]; // Remove query params
    let baseUrl = currentSrc;

    // Clean up existing suffixes to get back to "bar" (default)
    // Order matters: specific suffixes first
    baseUrl = baseUrl.replace('_pie.png', '.png').replace('_line.png', '.png');

    let newUrl = baseUrl;
    if (chartType === 'pie') {
        newUrl = baseUrl.replace('.png', '_pie.png');
    } else if (chartType === 'line') {
        newUrl = baseUrl.replace('.png', '_line.png');
    }

    console.log(`Switching ${chartName} to ${chartType}: ${newUrl}`);

    // Short delay to simulate processing (better UX)
    setTimeout(() => {
        img.onload = () => {
            loader.style.display = 'none';
            img.style.display = 'block';
        };
        img.onerror = () => {
            loader.innerHTML = `
                <i class="fas fa-exclamation-circle" style="color: var(--warning);"></i>
                <p class="text-muted" style="margin-top: 10px;">Not available for this chart.</p>
            `;
            setTimeout(() => {
                loader.style.display = 'none';
                img.style.display = 'block';
                img.src = baseUrl; // Revert to default
            }, 2000);
        };
        img.src = `${newUrl}?t=${new Date().getTime()}`;
    }, 600);
}

async function initDashboardCharts() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard`);
        const data = await response.json();
        if (!data.status === 'success') return;

        const stats = data.conversations_chart;
        const timeStats = data.time_saved_chart;

        // Conversations Chart
        const ctx1 = document.getElementById('conversationsChart').getContext('2d');
        new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    { label: 'Weekly', data: stats.weekly, backgroundColor: '#10B981', borderRadius: 4, barThickness: 8 },
                    { label: 'Monthly', data: stats.monthly, backgroundColor: '#A855F7', borderRadius: 4, barThickness: 8 },
                    { label: 'Yearly', data: stats.yearly, backgroundColor: '#3B82F6', borderRadius: 4, barThickness: 8 }
                ]
            },
            options: { maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });

        // Time Saved Chart
        const ctx2 = document.getElementById('timeSavedChart').getContext('2d');
        new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['P', 'B', 'O'],
                datasets: [{ data: timeStats.values, backgroundColor: ['#A855F7', '#3B82F6', '#F59E0B'], borderWidth: 0 }]
            },
            options: { cutout: '75%', maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });


        const centerText = document.querySelector('.donut-center .big-number');
        if (centerText) centerText.textContent = timeStats.total;

    } catch (e) {
        console.error('Charts error:', e);
    }
}

// ============================================
// CHAT FUNCTIONALITY
// ============================================
async function getDataOverview(sessionId) {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);

        const response = await fetch(`${API_BASE_URL}/chat/overview`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        const data = await response.json();
        if (response.ok && data.response) {
            // Clear chat and add overview
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                chatMessages.innerHTML = '';
                addChatMessage('assistant', data.response);
            }
        }
    } catch (error) {
        console.error('Overview error:', error);
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message || !currentSessionId) {
        if (!currentSessionId) {
            alert('Please upload a file first to start chatting about your data.');
        }
        return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
        openAuth('login');
        return;
    }

    // Add user message to chat
    addChatMessage('user', message);
    input.value = '';

    // Show loading
    const loadingId = addChatMessage('assistant', '💭 Thinking...');

    try {
        const formData = new FormData();
        formData.append('session_id', currentSessionId);
        formData.append('message', message);

        console.log('Sending chat message:', message);
        console.log('Session ID:', currentSessionId);

        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        console.log('Chat response status:', response.status);
        const data = await response.json();
        console.log('Chat response data:', data);

        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) loadingMsg.remove();

        if (response.ok && data.response) {
            addChatMessage('assistant', data.response);
        } else {
            // Show detailed error message
            const errorMsg = data.detail || data.message || 'Failed to get response';
            console.error('Chat API error:', errorMsg);
            addChatMessage('assistant', `❌ ${errorMsg}`);
        }
    } catch (error) {
        console.error('Chat error:', error);
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) loadingMsg.remove();

        // Show user-friendly error
        addChatMessage('assistant', `❌ Connection error: ${error.message || 'Please try again.'}`);
    }
}

function addChatMessage(role, content) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    const messageId = 'msg-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `chat-message ${role}-message`;

    // Format content (Basic Markdown to HTML)
    let formatted = content || '';

    // 1. Bold (**text**)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');

    // 2. Lists (- item) -> <li>item</li>
    if (formatted.includes('\n- ') || formatted.includes('\n* ')) {
        const lines = formatted.split('\n');
        let inList = false;
        let finalHtml = '';

        lines.forEach(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                if (!inList) {
                    finalHtml += '<ul>';
                    inList = true;
                }
                finalHtml += `<li>${trimmed.substring(2)}</li>`;
            } else {
                if (inList) {
                    finalHtml += '</ul>';
                    inList = false;
                }
                finalHtml += line + '<br>';
            }
        });
        if (inList) finalHtml += '</ul>';
        formatted = finalHtml;
    } else {
        formatted = formatted.replace(/\n/g, '<br>');
    }

    if (role === 'user') {
        messageDiv.innerHTML = `<div class="message-content">${formatted}</div><div class="message-avatar"><i class="fas fa-user"></i></div>`;
    } else {
        messageDiv.innerHTML = `<div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content">${formatted}</div>`;

        // Chips Logic
        setTimeout(() => {
            const listItems = messageDiv.querySelectorAll('li');
            listItems.forEach(li => {
                li.style.cursor = 'pointer';
                li.onclick = function () {
                    const text = this.innerText;
                    const input = document.getElementById('chat-input');
                    if (input) {
                        input.value = text;
                        if (typeof sendChatMessage === 'function') sendChatMessage();
                    }
                };
            });
        }, 0);
    }

    chatMessages.appendChild(messageDiv);

    const welcome = document.querySelector('.chat-welcome');
    if (welcome) welcome.style.display = 'none';

    setTimeout(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);

    return messageId;
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
});


// ============================================
// COLUMN MAPPING LOGIC
// ============================================
let mappingSourceData = null; // Stores data for mapping logic

function openMappingModal(data) {
    mappingSourceData = data;
    const container = document.getElementById("mapping-fields-container");
    container.innerHTML = "";

    // Create dropdowns for each missing concept
    data.missing_concepts.forEach(concept => {
        const div = document.createElement("div");
        div.className = "form-group";
        div.style.marginBottom = "1rem";

        // Clean label: "Sales Amount (e.g. Sales)" -> "Sales Amount"
        let label = concept;
        if (label.includes("(")) label = label.split("(")[0].trim();

        let options = data.columns.map(col => `<option value="${col}">${col}</option>`).join("");

        div.innerHTML = `
            <label style="display:block; margin-bottom:0.5rem; font-weight:600;">Which column is <strong>${label}</strong>?</label>
            <select class="form-control mapping-select" data-concept="${label}" required style="width:100%; padding:0.5rem; border:1px solid #ddd; border-radius:4px;">
                <option value="">-- Select Column --</option>
                ${options}
            </select>
            <small style="color:#666; display:block; margin-top:0.25rem;">Required for analysis</small>
        `;
        container.appendChild(div);
    });

    document.getElementById("mapping-modal").classList.add("active");
}

function closeMappingModal() {
    document.getElementById("mapping-modal").classList.remove("active");
}

function handleMappingSubmit(e) {
    e.preventDefault();

    const selects = document.querySelectorAll(".mapping-select");
    const mapping = {};

    selects.forEach(sel => {
        if (sel.value) {
            // Logic: User maps "MyStash" -> "Sales Amount"
            // We need to tell backend: Rename "MyStash" to something backend recognizes.
            // Backend recognizes: 'sales', 'revenue', 'amount'.
            // So we rename to "Mapped_Sales_Amount".

            const concept = sel.getAttribute("data-concept");
            let safeName = "Mapped_" + concept.replace(/[^a-zA-Z]/g, "") + "_Amount";
            // This ensures "Amount" keyword is present for Sales/Finance detection logic!

            if (concept.toLowerCase().includes("date")) {
                safeName = "Mapped_Date_Col"; // Ensure 'date' keyword present
            }

            mapping[sel.value] = safeName;
        }
    });

    console.log("Submitting Mapping:", mapping);
    closeMappingModal();

    // Resume analysis with mapping
    analyzeData(mapping);
}


async function downloadReport(id) {
    const token = localStorage.getItem('access_token');
    if (!token) return openAuth('login');

    const btn = event ? event.currentTarget : null;
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        btn.disabled = true;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/report/download/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Processing failed");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Analytix_Report_${id.slice(-6)}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error("Download error:", error);
        alert("Could not generate report. Check console.");
    } finally {
        if (btn) {
            btn.innerHTML = originalText; // Restore icon
            btn.disabled = false;
        }
    }
}


function showLoadingDashboard() {
    const container = document.getElementById('results-container');
    container.innerHTML = `
        <div class="dashboard-header" style="text-align: center; padding: 2rem; animation: fadeIn 0.5s;">
            <h2><i class="fas fa-rocket fa-bounce" style="color: var(--primary);"></i> Analyzing Your Data...</h2>
            <p class="text-muted">Our AI is crunching the numbers. Please wait.</p>
        </div>
        
        <div class="responsive-grid">
            <!-- Mock KPI Cards -->
            <div class="card" style="height: 120px; display: flex; align-items: center; justify-content: center; opacity: 0.7;">
                <i class="fas fa-circle-notch fa-spin" style="font-size: 2rem; color: var(--text-muted);"></i>
            </div>
            <div class="card" style="height: 120px; display: flex; align-items: center; justify-content: center; opacity: 0.7;">
                <i class="fas fa-circle-notch fa-spin" style="font-size: 2rem; color: var(--text-muted);"></i>
            </div>
            <div class="card" style="height: 120px; display: flex; align-items: center; justify-content: center; opacity: 0.7;">
                <i class="fas fa-circle-notch fa-spin" style="font-size: 2rem; color: var(--text-muted);"></i>
            </div>

            <!-- Mock Chart 1 -->
            <div class="card" style="height: 400px; grid-column: span 2; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px dashed var(--border-color);">
                <i class="fas fa-chart-pie fa-spin" style="font-size: 3rem; color: var(--primary); margin-bottom: 1rem; opacity: 0.5;"></i>
                <h4 style="color: var(--text-muted);">Generating Visuals...</h4>
            </div>
            
            <!-- Mock Chart 2 -->
            <div class="card" style="height: 400px; grid-column: span 2; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px dashed var(--border-color);">
                <i class="fas fa-chart-line fa-pulse" style="font-size: 3rem; color: var(--secondary); margin-bottom: 1rem; opacity: 0.5;"></i>
                <h4 style="color: var(--text-muted);">Calculating Trends...</h4>
            </div>
        </div>
    `;
    switchTab('analytics'); // Switch immediately
}


async function deleteHistoryItem(id) {
    if (!confirm("Are you sure you want to delete this analysis? This cannot be undone.")) return;

    const token = localStorage.getItem('access_token');
    if (!token) return openAuth('login');

    try {
        const response = await fetch(`${API_BASE_URL}/api/history/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            showToast('Item deleted successfully', 'success');
            loadHistory(); // Refresh list
        } else {
            showToast("Failed to delete item.", 'error');
        }
    } catch (error) {
        console.error("Delete error:", error);
    }
}

// ============================================
// CUSTOM REPORT DOWNLOAD
// ============================================
async function downloadCustomReport() {
    const btn = event ? event.currentTarget : null;
    const originalContent = btn ? btn.innerHTML : '';

    if (!currentReportId) {
        alert("Report ID not found. Please upload/analyze a file first.");
        return;
    }

    if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        btn.disabled = true;
    }

    try {
        // 1. Gather Preferences from current view
        const preferences = {};
        document.querySelectorAll('.field-chart-item').forEach(item => {
            const chartName = item.getAttribute('data-chart-name');
            const img = item.querySelector('img');

            if (chartName && img && img.src) {
                // Check if user selected Pie, Line, or Bar variant
                if (img.src.includes('_pie.png')) preferences[chartName] = 'pie';
                else if (img.src.includes('_line.png')) preferences[chartName] = 'line';
                else if (img.src.includes('_bar.png')) preferences[chartName] = 'bar';
                // else assumes default
            }
        });

        console.log("Generating Report for:", currentReportId);
        console.log("With Preferences:", preferences);

        const token = localStorage.getItem('access_token');

        const response = await fetch(`${API_BASE_URL}/api/report/custom_download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                report_id: currentReportId,
                preferences: preferences
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Report generation failed");
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Extract filename from header? Or manual
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'Analytix_Report.pdf';
        if (contentDisposition && contentDisposition.includes('filename=')) {
            filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
        }

        a.download = filename;
        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (e) {
        console.error("Custom download error:", e);
        alert(`Failed to generate custom report: ${e.message}`);
    } finally {
        if (btn) {
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    }
}


// ============================================
// LANDING OVERLAY & GUEST MODE LOGIC
// ============================================

// --- 1. Particle System ---
(function initParticles() {
    const canvas = document.getElementById('particles-landing');
    if (!canvas) return; // Dashboard might not have overlay if removed
    const ctx = canvas.getContext('2d');
    let particles = [];

    let mouse = { x: null, y: null, radius: 150 };

    window.addEventListener('mousemove', (event) => {
        mouse.x = event.x;
        mouse.y = event.y;
    });
    window.addEventListener('mouseout', () => { mouse.x = null; mouse.y = null; });

    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.size = Math.random() * 2 + 1;
            this.color = '#1e293b';
        }
        update() {
            this.x += this.vx; this.y += this.vy;
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

            if (mouse.x != null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < mouse.radius) {
                    const forceDirectionX = dx / distance;
                    const forceDirectionY = dy / distance;
                    const force = (mouse.radius - distance) / mouse.radius;
                    const directionX = forceDirectionX * force * 2;
                    const directionY = forceDirectionY * force * 2;
                    this.x += directionX;
                    this.y += directionY;
                }
            }
        }
        draw() {
            ctx.fillStyle = this.color; ctx.globalAlpha = 0.2;
            ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
        }
    }

    const particleCount = window.innerWidth > 768 ? 200 : 100; // Increased density significantly
    for (let i = 0; i < particleCount; i++) particles.push(new Particle());

    function animate() {
        if (!document.getElementById('landing-overlay')) return; // Stop if removed
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach((p, index) => {
            p.update(); p.draw();
            for (let j = index + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x; const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                // Increased connection distance and visibility
                if (dist < 200) {
                    // Stronger base opacity (was 0.1, now effectively up to 0.5)
                    const alpha = (1 - dist / 200) * 0.5;
                    ctx.strokeStyle = `rgba(30, 41, 59, ${alpha})`;
                    ctx.lineWidth = 0.8; // Slightly thicker lines
                    ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
                }
            }
            if (mouse.x != null) {
                let dx = mouse.x - p.x;
                let dy = mouse.y - p.y;
                let dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < mouse.radius) {
                    ctx.strokeStyle = `rgba(59, 130, 246, ${0.6 - dist / mouse.radius})`; // Stronger mouse connections
                    ctx.lineWidth = 1.5;
                    ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
                }
            }
        });
        requestAnimationFrame(animate);
    }
    animate();
})();

// --- 2. Typing Effect ---
(function initTyping() {
    const words = ["Sales", "Finance", "Growth", "Customers", "Future"];
    let i = 0;

    function typeWriter() {
        if (!document.getElementById('type-text')) return;
        const element = document.getElementById("type-text");
        const word = words[i];
        let current = element.innerText;

        if (current === word) { setTimeout(deleteWriter, 2000); return; }
        element.innerText = word.substring(0, current.length + 1);
        setTimeout(typeWriter, 150);
    }

    function deleteWriter() {
        if (!document.getElementById('type-text')) return;
        const element = document.getElementById("type-text");
        let current = element.innerText;
        if (current === "") { i = (i + 1) % words.length; typeWriter(); return; }
        element.innerText = current.substring(0, current.length - 1);
        setTimeout(deleteWriter, 100);
    }
    setTimeout(typeWriter, 1000);
})();

// --- 3. Transition Logic (FLIP Animation) ---
function startAnalyzing() {
    const landingLogo = document.getElementById('landing-logo');
    const sidebarLogo = document.querySelector('.sidebar .logo-text');

    if (!sidebarLogo) {
        console.error("Sidebar logo not found for animation target.");
        return;
    }

    // 1. Get Coordinates
    const startRect = landingLogo.getBoundingClientRect();
    const endRect = sidebarLogo.getBoundingClientRect();

    // 2. Prepare Element for Flight
    landingLogo.style.position = 'fixed';
    landingLogo.style.top = `${startRect.top}px`;
    landingLogo.style.left = `${startRect.left}px`;
    // width: auto allows the container to shrink naturally as font-size decreases
    landingLogo.style.width = 'auto';
    landingLogo.style.margin = '0';
    landingLogo.style.zIndex = '10001';
    landingLogo.style.transformOrigin = 'top left'; // Not needed for current approach but good safety
    landingLogo.style.whiteSpace = 'nowrap'; // Crucial to prevent wrapping during resize

    // CRITICAL FIX: Move to body so it doesn't fade out with the overlay
    document.body.appendChild(landingLogo);

    // Force Reflow
    void landingLogo.offsetWidth;

    // 3. Add Transition Class
    // Animate ALL properties (top, left, font-size) for true rendering update
    landingLogo.style.transition = 'all 0.8s cubic-bezier(0.19, 1, 0.22, 1)';

    // 4. Animate to Destination
    // sidebarLogo remains hidden/placeholder
    sidebarLogo.style.opacity = '0';

    // Move to position
    // Use easeOutExpo for a very precise "stick the landing" effect (no bounce, no overshoot)
    landingLogo.style.transition = 'all 0.8s cubic-bezier(0.19, 1, 0.22, 1)';
    landingLogo.style.top = `${endRect.top}px`;
    landingLogo.style.left = `${endRect.left}px`;

    // Explicitly Match Target Styles to preventing layout jump
    const targetStyles = getComputedStyle(sidebarLogo);
    landingLogo.style.fontSize = targetStyles.fontSize;
    landingLogo.style.fontWeight = '800'; // Ensure bold match
    landingLogo.style.lineHeight = targetStyles.lineHeight; // Critical for vertical alignment
    landingLogo.style.padding = targetStyles.padding;
    landingLogo.style.letterSpacing = targetStyles.letterSpacing;

    landingLogo.style.transform = 'none';

    // 5. Fade out Hero Content
    document.querySelector('.landing-subtext').classList.add('fade-out-content');
    document.querySelector('.landing-desc').classList.add('fade-out-content');
    document.querySelector('.landing-cta-group').classList.add('fade-out-content');
    document.querySelector('.landing-badge').classList.add('fade-out-content');

    // 6. DOM Transplant (The Ultimate seamless fix)
    setTimeout(() => {
        const overlay = document.getElementById('landing-overlay');
        overlay.classList.add('fade-out-overlay');

        // At the end of movement (0.8s), physically move the element
        setTimeout(() => {
            // 1. Prepare Target
            const targetContainer = sidebarLogo.parentElement;

            // 2. Clean current Logo styles to match Sidebar context
            landingLogo.style.position = '';
            landingLogo.style.top = '';
            landingLogo.style.left = '';
            landingLogo.style.width = '';
            landingLogo.style.margin = '';
            landingLogo.style.zIndex = '';
            landingLogo.style.transition = '';
            landingLogo.style.transform = '';

            // 3. Swap Classes
            landingLogo.className = sidebarLogo.className; // Adopt 'logo-text'
            landingLogo.id = ''; // Remove ID to avoid duplicates if re-run (though re-run impossible)

            // 4. Transplant
            sidebarLogo.remove(); // Remove static placeholder
            targetContainer.appendChild(landingLogo); // Insert our flying hero

            // 5. Final Cleanup
            overlay.style.display = 'none';
        }, 800);
    }, 100);
}

async function finalizeLogin() {
    const btn = document.querySelector('.btn-login-modal');
    const originalText = 'Sign In';
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Signing in...';
    btn.disabled = true;

    const email = document.getElementById('landing-email').value;
    const password = document.getElementById('landing-password').value;

    try {
        // Attempt Real Login (OAuth2 Standard)
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        // Try /token endpoint first (Standard for FastAPI/OAuth2)
        let response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            body: formData
        });

        // Fallback to /api/login if /token fails (just in case)
        if (!response.ok) {
            response = await fetch(`${API_BASE_URL}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
        }

        if (response.ok) {
            const data = await response.json();
            const token = data.access_token || data.token;

            if (token) {
                localStorage.setItem('access_token', token);
                localStorage.setItem('user_email', email);
                isGuestMode = false;

                // Hide Modal
                document.getElementById('login-modal').classList.remove('active');

                // Update UI
                const name = email.split('@')[0];
                document.getElementById('sidebar-user-name').textContent = name.charAt(0).toUpperCase() + name.slice(1);
                document.getElementById('sidebar-user-role').textContent = 'Pro Plan';

                // CRITICAL: Fetch History
                if (typeof loadHistory === 'function') {
                    console.log("Loading history after popup login...");
                    loadHistory();
                }

                showToast("Successfully Logged In!");
            } else {
                throw new Error("Authentication successful but no token received.");
            }
        } else {
            // Check for Demo credentials fallback (Frontend Simulation)
            if (email === 'demo@analytix.ai' && password === 'password') {
                isGuestMode = false;
                document.getElementById('login-modal').classList.remove('active');
                document.getElementById('sidebar-user-name').textContent = 'Demo User';
                showToast("Demo Mode Activated.");
            } else {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || "Invalid credentials");
            }
        }
    } catch (error) {
        console.error("Login Check Failed:", error);
        showToast(error.message, 'error');
    } finally {
        if (btn) {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }
}

// --- 4. Guest Mode Interceptor & Session Init ---
function checkAuth(actionName) {
    if (isGuestMode) {
        // Use the MAIN Auth Modal (Top Login) instead of custom one
        if (typeof openAuth === 'function') {
            openAuth('login');
        } else {
            console.error("openAuth function not found");
            alert("Please login to continue.");
        }
        return false;
    }
    return true;
}

// Session Check on Load
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (token) {
        console.log("Restoring active session...");
        isGuestMode = false;
        const email = localStorage.getItem('user_email') || 'User';
        const name = email.split('@')[0];

        // Update Sidebar
        const sidebarName = document.getElementById('sidebar-user-name');
        if (sidebarName) sidebarName.textContent = name.charAt(0).toUpperCase() + name.slice(1);

        const sidebarRole = document.getElementById('sidebar-user-role');
        if (sidebarRole) sidebarRole.textContent = 'Pro Plan';

        // Load History
        if (typeof loadHistory === 'function') loadHistory();
    }
});

// Add close handler for modal background click - REMOVED (Old Modal Deprecated)
// document.getElementById('login-modal')?.remove(); 

// Layout Toggle
function toggleLayout() {
    document.body.classList.toggle('layout-top-nav');
    if (document.body.classList.contains('layout-top-nav')) {
        document.querySelector('.sidebar').style.display = 'none';
        document.getElementById('top-logo').style.display = 'flex';
        document.getElementById('top-nav-links').style.display = 'flex';
        document.getElementById('page-title').style.display = 'none';
    } else {
        document.querySelector('.sidebar').style.display = 'flex';
        document.getElementById('top-logo').style.display = 'none';
        document.getElementById('top-nav-links').style.display = 'none';
        document.getElementById('page-title').style.display = 'block';
    }
}

// Toast Notification System
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };

    toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <div class="toast-message">${message}</div>
    `;

    container.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

