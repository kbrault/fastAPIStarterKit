// Configuration
const API_BASE_URL = "http://localhost:8080";
const REFRESH_TOKEN_EXPIRE_DAYS = 7;

// Cookie Utilities
const setCookie = (name, value, days) => {
    const expires = days 
        ? `; expires=${new Date(Date.now() + days * 864e5).toUTCString()}`
        : "";
    document.cookie = `${name}=${value}; path=/${expires}`;
};

const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    return parts.length === 2 ? parts.pop().split(";").shift() : undefined;
};

// Generic API Request
const apiRequest = async (endpoint, method = "POST", body = null, headers = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            ...headers
        },
        ...(body && { body: body.toString() })
    };

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return { status: response.status, data };
    } catch (error) {
        console.error("API Request Error:", error);
        return { status: "error", message: "Failed to connect to the server." };
    }
};

// API Wrappers
const login = (username, password) => {
    const body = new URLSearchParams({ username, password });
    return apiRequest("/api/login", "POST", body);
};

const refreshAccessToken = (refreshToken) =>
    apiRequest("/api/refresh-token", "POST", null, {
        "Authorization": `Bearer ${refreshToken}`
    });

const getProducts = (accessToken) =>
    apiRequest("/api/products", "GET", null, {
        "Authorization": `Bearer ${accessToken}`
    });

// Display Product List in Table
const displayProducts = (response) => {
    const productsList = document.getElementById("productsList");
    if (!productsList) return;

    if (response.status === 200 && response.data?.status === "success") {
        productsList.innerHTML = ""; // Clear loading row

        response.data.data.forEach(({ id, name, price, category }) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${id}</td>
                <td>${name}</td>
                <td>${price.toFixed(2)}€</td>
                <td>${category}</td>
            `;
            productsList.appendChild(row);
        });
    } else {
        console.error("Failed to fetch products:", response);
        window.location.href = "login.html";
    }
};

// Login Form Handler
const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const response = await login(username, password);
        if (response.status === 200 && response.data?.status === "success") {
            const { access_token, refresh_token } = response.data.data;
            sessionStorage.setItem("access_token", access_token);
            setCookie("refresh_token", refresh_token, REFRESH_TOKEN_EXPIRE_DAYS);
            window.location.href = "products.html";
        } else {
            alert("Login failed.");
        }
    });
}

// Protected Products Page Handler
const productsList = document.getElementById("productsList");
if (productsList) {
    const accessToken = sessionStorage.getItem("access_token");

    const loadProducts = (token) => getProducts(token).then(displayProducts);

    if (accessToken) {
        loadProducts(accessToken);
    } else {
        const refreshToken = getCookie("refresh_token");

        if (!refreshToken) {
            window.location.href = "login.html";
        } else {
            console.log("Attempting to refresh access token...");
            refreshAccessToken(refreshToken).then((response) => {
                if (response.status === 200 && response.data?.status === "success") {
                    const newAccessToken = response.data.data.access_token;
                    sessionStorage.setItem("access_token", newAccessToken);
                    loadProducts(newAccessToken);
                } else {
                    console.error("Refresh failed:", response);
                    window.location.href = "login.html";
                }
            });
        }
    }
}
