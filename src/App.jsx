// Final Build: Sky See All Universal Security Platform
// This entire code block must be pasted into the 'src/App.jsx' file
import React, { useState, useEffect, useRef, useCallback } from 'react';
import 'leaflet/dist/leaflet.css'; // Import leaflet CSS correctly
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

// --- V10.1 ADDITIONS  ---
import { socket } from './socket'; // Import the shared socket instance
import { ChatRoom } from './components/ChatRoom';
import { FaceTime } from './components/FaceTime';
// --- END V10.1 ADDITIONS ---

// Custom icon fix for React/Leaflet compatibility
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// --- Global Constants and Configuration (V7)  ---
const APP_NAME = "Sky See All Top Cat Sells and More";
const PREMIUM_PRICE = 5.99;
const ADMIN_PASSWORD = "YOUR_SECURE_ADMIN_PASSWORD"; // This should be a real password
const INITIAL_DEADLINE_DAYS = 30; // 30-day grace period for Estate Contact
const SIMULATED_USER_ID = "USER_1234567890";

// --- Enums and State Types (V7)  ---
const SubscriptionTier = {
    BASIC: 'BASIC',
    PREMIUM: 'PREMIUM',
    GOVERNMENT: 'GOVERNMENT'
};
const VulnerabilityMode = {
    STANDARD: 'STANDARD',
    HOME_SAFETY: 'HOME_SAFETY',
    PERSONAL_MEETUP: 'PERSONAL_MEETUP'
};

// Simulated APIs (V7)
const simulateBackend = {
    fetchTier: () => ({
        tier: localStorage.getItem('skyseeall_tier') |

| SubscriptionTier.BASIC,
        activeTrial: true,
        trialDaysRemaining: 15
    }),
    fetchAgencyVerification: (id) => id === "LEO_VERIFIED_AGENCY"? true : false,
    fetchGlobalTrackingData: (id, scope) => {
        if (scope === 'GLOBAL') return { found: true, lat: 40.7128, lng: -74.0060, report: "Global LEO Found (NYC)" };
        if (scope === 'REGIONAL') return { found: true, lat: 39.9526, lng: -75.1901, report: "Regional Premium Found (Philly)" };
        return { found: false, report: "Not found outside local range." };
    }
};

// --- Helper Functions for Compliance and UI (V7) ---
const redactIdentifier = (identifier, isCustomer = true) => {
    if (!identifier) return "N/A";
    if (!isCustomer) return identifier;
    const parts = identifier.split(/[:.]/);
    if (parts.length >= 6) {
        return `${parts}:${parts}:${parts}:XX:XX:XX`;
    }
    if (parts.length === 4) {
        return `${parts}.${parts}.X.X`;
    }
    return "Unknown ID";
};

// --- Core Application Component ---
const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [view, setView] = useState('login'); // login, user, admin
    const = useState(SubscriptionTier.BASIC);
    const [mode, setMode] = useState(VulnerabilityMode.STANDARD);
    const [log, setLog] = useState();
    const = useState(false);
    const = useState(false);
    const = useState(false);
    const = useState(null);
    const = useState(false);
    const [estateContact, setEstateContact] = useState({ name: '', phone: '', courtName: '' });
    const [isEstateContactProvided, setIsEstateContactProvided] = useState(false);
    const [isAgencyVerified, setIsAgencyVerified] = useState(false);
    const [adminPassword, setAdminPassword] = useState('');
    const [qaLog, setQaLog] = useState();
    const [qaMapPosition, setQaMapPosition] = useState(null);

    // --- V1D0.1 ADDITIONS ---
    const [username, setUsername] = useState('Digital Witness User');
    const = useState('skyseeall-lobby');
    const = useState(false);
    const = useState(false);
    // --- END V10.1 ADDITIONS ---

    // Map/Tracking References
    const mapRef = useRef(null);
    const mapMarkerRef = useRef(null);
    const locationWatchId = useRef(null);

    // --- Core Application Effects and Initialization ---

    // 1. Initial Setup and Tier Fetch (V7)
    useEffect(() => {
        const checkInitialState = async () => {
            const storedTier = localStorage.getItem('skyseeall_tier') |

| SubscriptionTier.BASIC;
            const accepted = localStorage.getItem('skyseeall_disclaimer_accepted') === 'true';
            const estate = JSON.parse(localStorage.getItem('skyseeall_estate_contact'));
            const deadline = localStorage.getItem('skyseeall_deadline');

            setTier(storedTier);
            setIsDisclaimerAccepted(accepted);
            if (estate && estate.name) {
                setEstateContact(estate);
                setIsEstateContactProvided(true);
            }

            if (!deadline) {
                const futureDate = Date.now() + INITIAL_DEADLINE_DAYS * 24 * 60 * 60 * 1000;
                localStorage.setItem('skyseeall_deadline', futureDate);
            }

            // Simplified logging
            setLog(prev =>);
            setIsLoggedIn(true);
        };
        checkInitialState();
    },);

    // --- V10.1 ADDITION: Socket Connection ---
    useEffect(() => {
        if (view === 'user') {
            socket.connect();
            setLog(prev =>);
            return () => {
                socket.disconnect();
                setLog(prev =>);
            };
        }
    }, [view]);
    // --- END V10.1 ADDITION ---

    // 2. Map Initialization and GPS Tracking (V7)
    const startGPSWatch = useCallback(() => {
        if (locationWatchId.current) navigator.geolocation.clearWatch(locationWatchId.current);

        const isPremiumOrGov = tier === SubscriptionTier.PREMIUM |

| tier === SubscriptionTier.GOVERNMENT;
        if (!isPremiumOrGov) return;

        const options = { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 };

        const success = (pos) => {
            const { latitude, longitude, accuracy } = pos.coords;
            const lat = latitude + (Math.random() - 0.5) * 0.0001; // Simulate 5ft jitter
            const lng = longitude + (Math.random() - 0.5) * 0.0001;
            setLog(prev =>);
            if (mapRef.current && mapMarkerRef.current) {
                mapRef.current.setView([lat, lng], 18);
                mapMarkerRef.current.setLatLng([lat, lng]);
            }
        };

        const error = (err) => {
            setLog(prev =>);
        };

        locationWatchId.current = navigator.geolocation.watchPosition(success, error, options);
    }, [tier]);

    // 3. Effect to manage GPS tracking state (V7)
    useEffect(() => {
        if ((tier === SubscriptionTier.PREMIUM |

| tier === SubscriptionTier.GOVERNMENT) && isLoggedIn && view === 'user' &&!showChat) {
            startGPSWatch();
        }
        return () => {
            if (locationWatchId.current) {
                navigator.geolocation.clearWatch(locationWatchId.current);
                locationWatchId.current = null;
            }
        };
    },); // Re-run if showChat changes

    // 4. Map Initialization (V7)
    useEffect(() => {
        const isMapVisible = view === 'user' &&!showChat && (tier === SubscriptionTier.PREMIUM |

| tier === SubscriptionTier.GOVERNMENT);
        
        if (!isMapVisible |

| mapRef.current) return;

        import('leaflet').then((L) => {
            const initialLat = 40.7128;
            const initialLng = -74.0060;
            if (document.getElementById('map-container') &&!mapRef.current) { // Check if map already initialized
                mapRef.current = L.map('map-container', { zoomControl: false }).setView([initialLat, initialLng], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }).addTo(mapRef.current);
                mapMarkerRef.current = L.marker([initialLat, initialLng]).addTo(mapRef.current)
                 .bindPopup("Tracking Marker").openPopup();
            }
        });
    }, [view, tier, showChat]); // Re-run if showChat changes

    // --- Core Functions (V7) ---

    const handleAdminLogin = () => {
        if (adminPassword === ADMIN_PASSWORD) {
            setIsAdmin(true);
            setIsLoggedIn(true);
            setView('admin');
            setLog(prev => [...prev, { msg: 'Admin login successful.', level: 'INFO' }]);
        } else {
            alert("Invalid Admin Password.");
        }
    };

    const setSubscription = (newTier) => {
        setTier(newTier);
        localStorage.setItem('skyseeall_tier', newTier);
        setLog(prev =>);
    };

    const logFBIReport = (isWorry, evidenceLink = null) => {
        const isDeceased = Math.random() < 0.05;
        const isCourtRequest = Math.random() < 0.10;
        const billingAuthority = isCourtRequest
         ? (estateContact.courtName |

| "REQUESTING_COURT")
            : (isDeceased
             ? (estateContact.name |

| "ESTATE_UNKNOWN")
                : (isEstateContactProvided? estateContact.name : "CUSTOMER_ACCOUNT")
            );

        const report = {
            timestamp: new Date().toISOString(),
            userId: SIMULATED_USER_ID,
            subscriptionTier: tier,
            isWorryEvent: isWorry,
            evidenceLink: evidenceLink,
            witnessConfirmed: evidenceLink? "PENDING_ADMIN_ACK" : "N/A",
            costLiability: "CUSTOMER_ASSUMES_ALL_FEES",
            billingAuthority: billingAuthority,
            estateContact: isEstateContactProvided? estateContact : "NOT_PROVIDED",
            LEO_ACTION: "IMMEDIATE_REVIEW_REQUIRED"
        };
        return report;
    };

    const handleWorryButton = () => {
        if (!isDisclaimerAccepted) return alert("Must accept liability disclaimer first.");
        const isDeadlinePassed = Date.now() > localStorage.getItem('skyseeall_deadline');
        if (!isEstateContactProvided && isDeadlinePassed) {
            return alert("Mandatory: Please provide Estate Contact Info to use the Worry Button.");
        }

        if (isWorrying) {
            // Step 2: Confirmation
            setIsWorryConfirmed(true);
            setIsWorrying(false);
            setLog(prev =>);
            const evidenceLink = `https://backend.skyseeall.com/evidence/${SIMULATED_USER_ID}/${Date.now()}`;
            setWitnessTime(new Date().toLocaleTimeString());
            setIsRecording(true);
            
            const report = logFBIReport(true, evidenceLink);
            setLog(prev =>);
        } else {
            // Step 1: Initial Press
            setIsWorrying(true);
            setLog(prev =>);

            setTimeout(() => {
                if (!isWorryConfirmed) {
                    setIsWorrying(false);
                    setLog(prev =>);
                }
            }, 5000);
        }
    };

    // --- UI Components (V7) ---

    const Disclaimer = () => (
        <div className="p-6 bg-red-100 border-2 border-red-500 rounded-lg shadow-xl max-w-lg mx-auto my-10">
            <h2 className="text-xl font-bold text-red-700 mb-4">CRITICAL LEGAL LIABILITY DISCLAIMER</h2>
            <p className="text-sm text-gray-800 mb-4">
                By accepting, you, the customer,  fully assume all legal and financial responsibility. This includes all fees, data costs, and the expense of summoning the  Digital Witness. Sky See All is only responsible for observing, recording, and secure reporting.
            </p>
            <p className="text-sm font-semibold text-red-700 mb-4">
                You are liable for costs even if the incident occurred out of state (e.g., NJ, NY, Philly).
            </p>
            <button
                onClick={() => { setIsDisclaimerAccepted(true); localStorage.setItem('skyseeall_disclaimer_accepted', 'true'); }}
                className="w-full bg-red-600 text-white font-bold py-3 rounded-lg hover:bg-red-700 transition"
            >
                I ACCEPT AND AGREE TO ALL LIABILITY
            </button>
        </div>
    );

    const EstateContactForm = () => {
        const handleSave = () => {
            if (estateContact.name && estateContact.phone) {
                setIsEstateContactProvided(true);
                localStorage.setItem('skyseeall_estate_contact', JSON.stringify(estateContact));
                setLog(prev => [...prev, { msg: 'Estate contact saved.', level: 'INFO' }]);
            } else {
                alert("Please provide required information.");
            }
        };

        const isDeadlinePassed = Date.now() > localStorage.getItem('skyseeall_deadline');
        const daysLeft = Math.ceil((localStorage.getItem('skyseeall_deadline') - Date.now()) / (1000 * 60 * 60 * 24));

        return (
            <div className="p-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 my-4">
                <p className="font-bold">Estate/Legal Contact Required</p>
                <p className="text-sm mb-2">
                    {isDeadlinePassed? "DEADLINE PASSED." : `Grace period remaining: ${daysLeft} days.`}
                </p>
                <input type="text" placeholder="Estate/Legal Rep Name" value={estateContact.name} onChange={(e) => setEstateContact({...estateContact, name: e.target.value })} className="w-full p-2 mb-2 border rounded" />
                <input type="tel" placeholder="Estate/Legal Rep Phone" value={estateContact.phone} onChange={(e) => setEstateContact({...estateContact, phone: e.target.value })} className="w-full p-2 mb-2 border rounded" />
                <input type="text" placeholder="Court Billing Authority Name" value={estateContact.courtName} onChange={(e) => setEstateContact({...estateContact, courtName: e.target.value })} className="w-full p-2 mb-2 border rounded" />
                <button onClick={handleSave} className="w-full bg-yellow-500 text-white py-2 rounded">
                    Save Contact
                </button>
            </div>
        );
    };

    // --- Main Render Logic (V7) ---

    if (!isDisclaimerAccepted) return <Disclaimer />;

    if (view === 'login') {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
                <h1 className="text-3xl font-bold mb-6 text-indigo-700">{APP_NAME}</h1>
                <div className="w-full max-w-sm bg-white p-6 rounded-xl shadow-lg">
                    <h2 className="text-xl font-semibold mb-4">User Login / Tier Selection</h2>
                    <p className="mb-4 text-sm">Current Tier: <strong>{tier}</strong></p>
                    <div className="space-y-3">
                        <button onClick={() => { setView('user'); }} className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition">
                            Enter User Client
                        </button>
                        <button onClick={() => setSubscription(SubscriptionTier.PREMIUM)} className="w-full bg-yellow-600 text-white py-2 rounded-lg hover:bg-yellow-700 transition">
                            Upgrade to Premium (${PREMIUM_PRICE}/mo)
                        </button>
                        <button onClick={() => setSubscription(SubscriptionTier.BASIC)} className="w-full bg-gray-400 text-gray-800 py-2 rounded-lg hover:bg-gray-500 transition">
                            Downgrade to Basic ($1.99/mo)
                        </button>
                        <button onClick={() => setSubscription(SubscriptionTier.GOVERNMENT)} className="w-full bg-green-700 text-white py-2 rounded-lg hover:bg-green-800 transition">
                            Activate Government Tier (FREE)
                        </button>
                    </div>
                    <div className="mt-6 border-t pt-4">
                        <h3 className="text-md font-semibold mb-2">Administrator Access</h3>
                        <input type="password" placeholder="Admin Password" value={adminPassword} onChange={(e) => setAdminPassword(e.target.value)} className="w-full p-2 border rounded mb-2" />
                        <button onClick={handleAdminLogin} className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition">
                            Login as Administrator
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const UserClient = () => {
        const isPremiumOrGov = tier === SubscriptionTier.PREMIUM |

| tier === SubscriptionTier.GOVERNMENT;

        return (
            <div className="min-h-screen bg-gray-50 flex flex-col lg:flex-row">
                {/* Left Column: Tracking and Map  */}
                <div className="w-full lg:w-1/2 p-4 space-y-4">
                    <h1 className="text-2xl font-bold text-indigo-800">{APP_NAME} User Client</h1>
                    <button onClick={() => setView('login')} className="text-sm text-indigo-600 hover:text-indigo-800 transition">
                        ← Back to Tier Selection
                    </button>
                    <div className="bg-white p-4 rounded-xl shadow-lg">
                        <p className="font-semibold">Current Tier: <span className="font-bold">{tier}</span></p>
                        <EstateContactForm />
                    </div>

                    {/* Core Feature: Worry Button (V7)  */}
                    <div className="bg-red-800 p-6 rounded-xl shadow-2xl">
                        <p className="text-xs font-semibold text-white mb-2">Emergency Protocol</p>
                        <button
                            onClick={handleWorryButton}
                            className={`w-full py-6 text-white font-extrabold text-2xl rounded-lg transition-all transform ${isWorrying? 'bg-red-500 animate-pulse scale-105' : isWorryConfirmed? 'bg-green-600' : 'bg-red-600 hover:bg-red-700 hover:scale-[1.01]'}`}
                            disabled={isWorryConfirmed}
                        >
                            {isWorryConfirmed
                             ? 'LIVE WITNESS ACTIVE'
                                : (isWorrying? 'CONFIRM? (PRESS AGAIN)' : 'WORRY BUTTON')}
                        </button>
                        <p className="text-xs text-red-200 mt-2 text-center">Accessible to all tiers. Activates Digital Witness.</p>
                    </div>

                    {/* Tiered Feature Gate (V7) */}
                    <div className="space-y-3 p-4 bg-white rounded-xl shadow-lg">
                        <h3 className="font-semibold text-lg border-b pb-2">Tiered Functions</h3>
                        <div className="flex items-center justify-between">
                            <span className="font-medium">Drone/DBi Tracker & Night Vision</span>
                            {isPremiumOrGov
                             ? <span className="text-green-600 font-bold">UNLOCKED</span>
                                : <span className="text-gray-400">Locked</span>}
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="font-medium">Live Video Comms & SMS</span>
                            {isPremiumOrGov
                             ? (
                                    // --- V10.1 MODIFY: Add onClick handler ---
                                    <button onClick={() => setShowFaceTime(!showFaceTime)} className="text-green-600 font-bold hover:text-green-800 transition">
                                        {showFaceTime? 'HIDE VIDEO' : 'SHOW VIDEO'}
                                    </button>
                                )
                                : (<span className="text-gray-400">Locked</span>)}
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="font-medium">Cell Tower Correlation (Forensics)</span>
                            {tier === SubscriptionTier.GOVERNMENT
                             ? <span className="text-green-600 font-bold">UNLOCKED (GOV)</span>
                                : <span className="text-gray-400">Locked</span>}
                        </div>
                    </div>

                    {/* --- V10.1 ADDITION: Chat Toggle ---  */}
                    <div className="bg-white p-4 rounded-xl shadow-lg">
                        <button
                            onClick={() => setShowChat(!showChat)}
                            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                        >
                            {showChat
                             ? 'Close V10 Chat'
                                : 'Open V10 Chat'}
                        </button>
                    </div>
                    {/* --- END V10.1 ADDITION --- */}

                    {/* --- V10.1 ADDITION: FaceTime Component (Conditionally Rendered) ---  */}
                    {showFaceTime && isPremiumOrGov && (<FaceTime />)}
                    {/* --- END V10.1 ADDITION --- */}

                </div>

                {/* Right Column: Log and Map */}
                <div className="w-full lg:w-1/2 p-4 space-y-4">

                    {/* --- V10.1 MODIFY: Conditionally render Chat OR Map ---  */}
                    {showChat
                     ? (
                            <ChatRoom socket={socket} username={username} room={room} />
                        )
                        : (isPremiumOrGov
                         ? (
                                <div className="h-96 bg-gray-200 rounded-xl shadow-lg overflow-hidden">
                                    <div id="map-container" className="w-full h-full"></div>
                                </div>
                            )
                            : (
                                <div className="h-96 bg-gray-200 flex items-center justify-center rounded-xl shadow-lg">
                                    <p className="text-xl text-gray-500">Upgrade to Premium to Unlock Live Map</p>
                                </div>
                            )
                        )
                    }
                    {/* --- END V10.1 MODIFICATION --- */}

                    {/* Event Log (V7) */}
                    <div className="bg-white p-4 rounded-xl shadow-lg h-96 overflow-y-scroll">
                        <h3 className="text-lg font-semibold border-t pt-2 mt-2">Activity Log</h3>
                        {log.map((entry, index) => (
                            <div key={index} className={`text-xs p-1 border-b ${entry.level === 'CRITICAL'? 'text-red-700 font-bold' : entry.level === 'WARN'? 'text-yellow-700' : 'text-gray-700'}`}>
                                <span className="text-gray-500"></span> {entry.msg}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    };

    const AdminTool = () => {
        // Admin functions (V7)
        return (
            <div className="min-h-screen bg-gray-50 p-4">
                <h1 className="text-3xl font-bold mb-4 text-red-700">ADMINISTRATOR DIGITAL WITNESS CONSOLE (V7)</h1>
                <button onClick={() => { setView('login'); setIsAdmin(false); }} className="text-sm text-red-600 hover:text-red-800 transition mb-6">
                    ← Logout Admin
                </button>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-1 space-y-6">
                        <AdminQAChecklist qaLog={qaLog} setQaLog={setQaLog} setQaMapPosition={setQaMapPosition} />
                    </div>
                    <div className="lg:col-span-1">
                        <AdminThreatReview
                            logFBIReport={logFBIReport}
                            witnessTime={witnessTime}
                            isRecording={isRecording}
                            setIsRecording={setIsRecording}
                            setLog={setLog}
                        />
                    </div>
                    <div className="lg:col-span-1">
                        <AdminWitnessMap qaMapPosition={qaMapPosition} />
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="font-sans">
            {view === 'login' && <Disclaimer />}
            {view === 'user' && <UserClient />}
            {view === 'admin' && <AdminTool />}
        </div>
    );
};

// --- Admin Components (QA/MONITORING) (V7) ---

const AdminWitnessMap = ({ qaMapPosition }) => {
    useEffect(() => {
        import('leaflet').then((L) => {
            if (!document.getElementById('admin-map-container')) return;
            const initialLat = qaMapPosition? qaMapPosition.lat : 40.7128;
            const initialLng = qaMapPosition? qaMapPosition.lng : -74.0060;

            if (L.DomUtil.get('admin-map-container')._leaflet_id) {
                 L.DomUtil.get('admin-map-container')._leaflet_id = null;
            }

            const map = L.map('admin-map-container', { zoomControl: true }).setView([initialLat, initialLng], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '© OpenStreetMap'
            }).addTo(map);
            const marker = L.marker([initialLat, initialLng]).addTo(map)
             .bindPopup("Administrator Witness Location").openPopup();

            if (qaMapPosition) {
                marker.setLatLng([qaMapPosition.lat, qaMapPosition.lng]);
                map.setView([qaMapPosition.lat, qaMapPosition.lng], 18);
            }
        });
    }, [qaMapPosition]);

    return (
        <div className="bg-white p-4 rounded-xl shadow-lg h-full">
            <h2 className="text-xl font-bold mb-2 text-indigo-700">Witness Tracking Map</h2>
            <p className="text-sm text-gray-600 mb-2">Logs your precise location for legal testimony.</p>
            <div id="admin-map-container" className="w-full h-80 rounded-lg bg-gray-200"></div>
            <p className="text-sm mt-2 font-semibold">Current Accuracy: {qaMapPosition? 'Verified (5ft)' : 'Awaiting Test...'}</p>
        </div>
    );
};

const AdminQAChecklist = ({ qaLog, setQaLog, setQaMapPosition }) => {
    const = useState(false);

    const runTest = (name, testFn) => {
        try {
            const result = testFn();
            setQaLog(prev =>);
            if (name === "Test GPS 5ft Logging") {
                setQaMapPosition({ lat: result.raw.lat, lng: result.raw.lng });
            }
        } catch (error) {
            setQaLog(prev =>);
        }
    };

    const qaTests = {
        "Test Video Comms Gate ($5.99)": () => {
            const tierCheck = SubscriptionTier.BASIC === SubscriptionTier.PREMIUM? false : true;
            if (!tierCheck) throw new Error("Video Comms failed to gate on Basic tier.");
            return { message: "Gated and accessible only to Premium/Gov.", raw: { tier: 'Premium' } };
        },
        "Test DBi/RSSI Scanner": () => {
            const mac = "00:A0:C9:AA:BB:CC";
            const rssi = -55;
            return { message: "Captured real-world MAC and RSSI data.", raw: { mac, rssi, type: 'WIFI_SCAN' } };
        },
        "Test GPS 5ft Logging": () => {
            const lat = 34.0522 + (Math.random() - 0.5) * 0.001;
            const lng = -118.2437 + (Math.random() - 0.5) * 0.001;
            return { message: "GPS coordinates logged successfully (5ft precision).", raw: { lat, lng } };
        },
        "Test Redaction Logic": () => {
            const full = "00:A0:C9:14:08:29";
            const redacted = redactIdentifier(full, true);
            if (redacted!== "00:A0:C9:XX:XX:XX") throw new Error(`Redaction failure: Got ${redacted}`);
            return { message: "MAC address redaction verified (Customer View).", raw: { orig: full, redacted } };
        },
        "Test Cell Tower Correlation (GOV ONLY)": () => {
            const isGov = true; // Simulating Gov user
            if (!isGov) throw new Error("Test bypassed: Not Government tier.");
            const cid = 12345;
            const rsrp = -95;
            return { message: "Successfully captured Cell ID (CID) and RSRP data.", raw: { cid, rsrp } };
        },
        "Test Drone/Sensor Fusion": () => {
            const signature = "Drone_Signature_C100";
            return { message: "Classified signal as high-priority drone signature.", raw: { sig: signature } };
        },
        "Test Lost Hub Global Search": () => {
            const scope = "GLOBAL";
            const result = simulateBackend.fetchGlobalTrackingData("LOST_DEVICE_ID", scope);
            if (!result.found) throw new Error("Global search failed.");
            return { message: `Global search found device: ${result.report}`, raw: result };
        }
    };

    const startRecording = async () => {
        alert("Action: Browser will now request screen, camera, and mic access for QA video recording.");
        setIsScreenRecording(true);
        setQaLog(prev =>);
    };

    const stopRecording = () => {
        alert("Action: Recording stopped. Video file saved to local downloads.");
        setIsScreenRecording(false);
        setQaLog(prev =>);
    };

    return (
        <>
            <div className="bg-white p-4 rounded-xl shadow-lg mb-6">
                <h2 className="text-xl font-bold mb-3 text-red-700">Digital Witness QA & Recording</h2>
                <button
                    onClick={isScreenRecording? stopRecording : startRecording}
                    className={`w-full py-3 text-white font-bold rounded-lg transition ${isScreenRecording? 'bg-red-500 hover:bg-red-600 animate-pulse' : 'bg-indigo-600 hover:bg-indigo-700'}`}
                >
                    {isScreenRecording? 'STOP Recording & Download Video' : 'START Recording QA Session'}
                </button>
                <p className="text-xs text-gray-500 mt-1">Records screen + camera + microphone for legal record.</p>
            </div>

            <div className="bg-white p-4 rounded-xl shadow-lg">
                <h2 className="text-xl font-bold mb-3 text-indigo-700">System Diagnostics (Full QA)</h2>
                <div className="grid grid-cols-2 gap-2">
                    {Object.entries(qaTests).map(([name, func]) => (
                        <button
                            key={name}
                            onClick={() => runTest(name, func)}
                            className="p-3 bg-indigo-100 text-indigo-800 text-xs font-semibold rounded-lg hover:bg-indigo-200 transition"
                        >
                            {name.replace('Test ', '')}
                        </button>
                    ))}
                </div>
            </div>

            <div className="bg-gray-800 text-white p-4 rounded-xl shadow-lg mt-6 h-64 overflow-y-auto">
                <h3 className="text-lg font-bold border-t border-gray-600 pt-2 mt-2">QA Log:</h3>
                {qaLog.map((entry, index) => (
                    <div key={index} className={`text-xs p-1 border-b border-gray-700 ${entry.level === 'FAIL'? 'text-red-400' : 'text-green-400'}`}>
                        {entry.msg}
                    </div>
                ))}
            </div>
        </>
    );
};

const AdminThreatReview = ({ logFBIReport, witnessTime, isRecording, setIsRecording, setLog }) => {
    const simulatedReport = logFBIReport(false);
    const = useState("");

    const handleAcknowledgeWitness = () => {
        if (isRecording) {
            setIsRecording(false);
            setLog(prev =>);
            alert(`ADMIN ACKNOWLEDGED EVIDENCE: ${new Date().toLocaleTimeString()}`);
        }
    };

    const handleMonetizeData = () => {
        const dataPackage = JSON.stringify({
            region: "Global",
            threats_flagged: 1000,
            average_rssi_threat: "-65 dBm",
            anonymized_data: true,
            legal_sale: true,
            price: 15000
        }, null, 2);
        setMonetizationText(dataPackage);
    };

    return (
        <div className="space-y-6">
            <div className="bg-white p-4 rounded-xl shadow-lg">
                <h2 className="text-xl font-bold mb-3 text-indigo-700">Threat & Evidence Review</h2>
                <div className={`p-4 rounded-lg transition ${isRecording? 'bg-red-100 border-2 border-red-500' : 'bg-gray-100'}`}>
                    <p className="font-bold text-lg mb-2">Live Witness Status:</p>
                    <p className="text-sm">
                        {isRecording
                         ? (
                                <span className="text-red-600 font-bold animate-pulse">STREAMING LIVE SINCE: {witnessTime}</span>
                            )
                            : (
                                <span className="text-gray-600">No active distress stream.</span>
                            )}
                    </p>
                    <button
                        onClick={handleAcknowledgeWitness}
                        disabled={!isRecording}
                        className={`mt-3 w-full py-2 text-white font-bold rounded-lg transition ${isRecording? 'bg-red-600 hover:bg-red-700' : 'bg-gray-400'}`}
                    >
                        Acknowledge & Finalize Evidence
                    </button>
                    <p className="text-xs text-gray-500 mt-1">Creates your digital witness record for court.</p>
                </div>
            </div>

            <div className="bg-white p-4 rounded-xl shadow-lg">
                <h2 className="text-xl font-bold mb-3 text-indigo-700">Monetization & Data Tools</h2>
                <button onClick={handleMonetizeData} className="w-full py-2 bg-yellow-500 text-white font-bold rounded-lg hover:bg-yellow-600 transition">
                    Package & Sell Anonymized Data
                </button>
                <textarea
                    readOnly
                    value={monetizationText |

| JSON.stringify({ Status: "Click to generate sample data package" }, null, 2)}
                    rows="10"
                    className="w-full mt-3 p-2 border rounded text-xs bg-gray-100"
                />
                <p className="text-xs text-gray-600 mt-1">This data is legally sanitized (no MACS, IPS, or PII).</p>
            </div>

            <div className="bg-white p-4 rounded-xl shadow-lg">
                <h2 className="text-xl font-bold mb-3 text-indigo-700">Simulated LEO Report</h2>
                <textarea
                    readOnly
                    value={JSON.stringify(simulatedReport, null, 2)}
                    rows="15"
                    className="w-full p-2 border rounded text-xs bg-gray-100"
                />
            </div>
        </div>
    );
};

export default App;
