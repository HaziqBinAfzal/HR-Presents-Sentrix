/*
====================================================
CodeSentinel AI
Global JavaScript
Part 1
====================================================
*/

"use strict";

/*
====================================================
DOM Elements
====================================================
*/

const sidebar = document.querySelector(".sidebar");
const sidebarToggle = document.querySelector("#sidebarToggle");
const mobileMenu = document.querySelector(".navbar-toggler");
const spinner = document.querySelector(".spinner-overlay");

/*
====================================================
Sidebar Toggle
====================================================
*/

function toggleSidebar() {

    if (!sidebar) return;

    sidebar.classList.toggle("active");

}

/*
====================================================
Close Sidebar
====================================================
*/

function closeSidebar() {

    if (!sidebar) return;

    sidebar.classList.remove("active");

}

/*
====================================================
Loading Spinner
====================================================
*/

function showSpinner() {

    if (!spinner) return;

    spinner.style.display = "flex";

}

function hideSpinner() {

    if (!spinner) return;

    spinner.style.display = "none";

}

/*
====================================================
Smooth Scroll
====================================================
*/

function smoothScroll(target) {

    const section = document.querySelector(target);

    if (!section) return;

    section.scrollIntoView({

        behavior: "smooth"

    });

}

/*
====================================================
Back To Top
====================================================
*/

function backToTop() {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}

/*
====================================================
Page Loader
====================================================
*/

window.addEventListener("load", function () {

    hideSpinner();

});

/*
====================================================
Resize Event
====================================================
*/

window.addEventListener("resize", function () {

    if (window.innerWidth > 992) {

        closeSidebar();

    }

});

/*
====================================================
Button Events
====================================================
*/

if (sidebarToggle) {

    sidebarToggle.addEventListener("click", toggleSidebar);

}

if (mobileMenu) {

    mobileMenu.addEventListener("click", toggleSidebar);

}

/*
====================================================
Console Message
====================================================
*/

console.log("CodeSentinel AI Loaded Successfully");

/*
====================================================
Toast Notification
====================================================
*/

function showToast(message, type = "success") {

    const toast = document.createElement("div");

    toast.className = `alert alert-${type} position-fixed`;

    toast.style.top = "20px";
    toast.style.right = "20px";
    toast.style.zIndex = "9999";
    toast.style.minWidth = "300px";

    toast.innerHTML = `
        <strong>${message}</strong>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.remove();

    }, 3000);

}

/*
====================================================
Password Visibility Toggle
====================================================
*/

function togglePassword(inputId, iconId) {

    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);

    if (!input || !icon) return;

    if (input.type === "password") {

        input.type = "text";

        icon.classList.remove("fa-eye");

        icon.classList.add("fa-eye-slash");

    } else {

        input.type = "password";

        icon.classList.remove("fa-eye-slash");

        icon.classList.add("fa-eye");

    }

}

/*
====================================================
Simple Form Validation
====================================================
*/

function validateRequired(formId) {

    const form = document.getElementById(formId);

    if (!form) return true;

    let valid = true;

    const fields = form.querySelectorAll("[required]");

    fields.forEach(field => {

        if (field.value.trim() === "") {

            field.classList.add("is-invalid");

            valid = false;

        } else {

            field.classList.remove("is-invalid");

            field.classList.add("is-valid");

        }

    });

    return valid;

}

/*
====================================================
Email Validation
====================================================
*/

function validateEmail(email) {

    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return pattern.test(email);

}

/*
====================================================
Password Strength
====================================================
*/

function passwordStrength(password) {

    let score = 0;

    if (password.length >= 8) score++;

    if (/[A-Z]/.test(password)) score++;

    if (/[a-z]/.test(password)) score++;

    if (/[0-9]/.test(password)) score++;

    if (/[^A-Za-z0-9]/.test(password)) score++;

    return score;

}

/*
====================================================
File Upload Preview
====================================================
*/

function previewFile(input) {

    if (!input.files.length) return;

    const file = input.files[0];

    console.log("Selected File:");

    console.log(file.name);

    console.log(file.size + " bytes");

    console.log(file.type);

}

/*
====================================================
Drag and Drop Upload
====================================================
*/

const uploadBox = document.querySelector(".upload-box");

if (uploadBox) {

    uploadBox.addEventListener("dragover", function(e){

        e.preventDefault();

        uploadBox.classList.add("border-primary");

    });

    uploadBox.addEventListener("dragleave", function(){

        uploadBox.classList.remove("border-primary");

    });

    uploadBox.addEventListener("drop", function(e){

        e.preventDefault();

        uploadBox.classList.remove("border-primary");

        showToast("File Ready for Upload");

    });

}

/*
====================================================
Search Filter
====================================================
*/

function filterTable(inputId, tableId) {

    const input = document.getElementById(inputId);

    const table = document.getElementById(tableId);

    if (!input || !table) return;

    const filter = input.value.toLowerCase();

    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {

        const row = rows[i];

        const text = row.textContent.toLowerCase();

        row.style.display = text.includes(filter) ? "" : "none";

    }

}

/*
====================================================
Confirmation Dialog
====================================================
*/

function confirmAction(message) {

    return confirm(message);

}

/*
====================================================
Copy Text
====================================================
*/

function copyText(text) {

    navigator.clipboard.writeText(text);

    showToast("Copied Successfully");

}

/*
====================================================
Success Message
====================================================
*/

console.log("JavaScript Part 2 Loaded");

/*
====================================================
Dark Mode
====================================================
*/

function toggleDarkMode() {

    document.body.classList.toggle("dark-mode");

    const enabled = document.body.classList.contains("dark-mode");

    localStorage.setItem("darkMode", enabled);

}

function loadDarkMode() {

    const enabled = localStorage.getItem("darkMode");

    if (enabled === "true") {

        document.body.classList.add("dark-mode");

    }

}

/*
====================================================
Animated Counter
====================================================
*/

function animateCounter(element, target) {

    let current = 0;

    const increment = Math.max(1, Math.ceil(target / 100));

    const timer = setInterval(() => {

        current += increment;

        if (current >= target) {

            current = target;

            clearInterval(timer);

        }

        element.textContent = current;

    }, 20);

}

/*
====================================================
Animate Dashboard Counters
====================================================
*/

function initializeCounters() {

    const counters = document.querySelectorAll(".counter");

    counters.forEach(counter => {

        const target = parseInt(counter.dataset.target);

        if (!isNaN(target)) {

            animateCounter(counter, target);

        }

    });

}

/*
====================================================
Progress Bar Animation
====================================================
*/

function animateProgressBars() {

    const progressBars = document.querySelectorAll(".progress-bar");

    progressBars.forEach(bar => {

        const width = bar.dataset.width;

        if (width) {

            bar.style.width = width + "%";

        }

    });

}

/*
====================================================
Scroll Animation
====================================================
*/

function revealOnScroll() {

    const items = document.querySelectorAll(".fade-in");

    const trigger = window.innerHeight * 0.9;

    items.forEach(item => {

        const top = item.getBoundingClientRect().top;

        if (top < trigger) {

            item.classList.add("show");

        }

    });

}

/*
====================================================
Disable Buttons During Form Submit
====================================================
*/

function disableSubmitButton(formId) {

    const form = document.getElementById(formId);

    if (!form) return;

    form.addEventListener("submit", function () {

        const button = form.querySelector("button[type='submit']");

        if (button) {

            button.disabled = true;

            button.innerHTML = "Please Wait...";

        }

    });

}

/*
====================================================
Auto Hide Alerts
====================================================
*/

function autoHideAlerts() {

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(alert => {

        setTimeout(() => {

            alert.style.opacity = "0";

            setTimeout(() => {

                alert.remove();

            }, 500);

        }, 4000);

    });

}

/*
====================================================
Current Year
====================================================
*/

function updateFooterYear() {

    const year = document.querySelector("#currentYear");

    if (year) {

        year.textContent = new Date().getFullYear();

    }

}

/*
====================================================
Page Initialization
====================================================
*/

document.addEventListener("DOMContentLoaded", function () {

    loadDarkMode();

    initializeCounters();

    animateProgressBars();

    autoHideAlerts();

    updateFooterYear();

    revealOnScroll();

});

/*
====================================================
Scroll Event
====================================================
*/

window.addEventListener("scroll", revealOnScroll);

/*
====================================================
Keyboard Shortcut
Ctrl + /
====================================================
*/

document.addEventListener("keydown", function (event) {

    if (event.ctrlKey && event.key === "/") {

        event.preventDefault();

        console.log("Keyboard shortcut activated.");

    }

});

/*
====================================================
Application Ready
====================================================
*/

console.log("CodeSentinel AI JavaScript Initialized Successfully");
