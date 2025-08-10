## Introduction  
This is a local web-based event booking application.  
It is a lightweight event booking system built using Flask, Bootstrap, and SQLite.

# 🎟️ Easy Booking – Event Management Frontend

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 📌 Overview
**Easy Booking** is a responsive, modern web interface for **event discovery, booking, and management**.  
It allows:
- **Users** to browse and book events.
- **Organizers** to launch and promote events.  

The design is clean, mobile-friendly, and ready for **backend integration**.

---

## ✨ Features

### 🔹 Navigation Bar
- Fixed top navigation.
- Links: Home, Discover, News, About Us, Blogs.
- **Sign In** and **Sign Up** modals without page reload.

### 🔹 Hero Section
- Headline + Description.
- "Launch Event" & "Book Event" buttons.
- Responsive image & text layout.

### 🔹 Search Section
- Search by name, location, category, and guest count.
- Styled floating card with shadow.

### 🔹 Event Listings
- Upcoming Events with:
  - Image, title, location, price, guests, rating.
  - "Book Now" button + quick action icons.
- Events Near You banner card with overlay CTA.

### 🔹 Email Subscription
- Styled subscription box with email input and button.

### 🔹 Authentication Modals
- **Sign In:** User/Organizer toggle.
- **Sign Up:** Separate forms for Users & Organizers.
- Organizers can add category, skills, and bio.

### 🔹 Footer
- Simple copyright.

---

## 🛠️ Tech Stack

- **HTML5** – Semantic structure.
- **CSS3** – Custom styles (`style.css`, `index.css`).
- **Bootstrap 5** – Responsive grid & components.
- **Font Awesome** – Icons for UI.
- **JavaScript (`account.js`)** – Toggles forms and modals.

---

## 📂 Folder Structure
Easy-Booking/
│── index.html # Main homepage
│── src/
│ ├── css/
│ │ ├── style.css # Theme styles
│ │ ├── index.css # Homepage-specific styles
│ ├── img/ # Logo & event images
│── fun/
│ ├── account.js # JS logic for forms

yaml
Copy
Edit

---

## 🎨 Theme Colors
| Role         | Color Code  |
|--------------|------------|
| Primary      | `#283747`  |
| Secondary    | `#FF7F50`  |
| Text         | `#FFFFFF`  |
| Background   | `ghostwhite` |
| Secondary Text | `#A1A1A1` |

---

## 📱 Responsiveness
- Mobile-first design.
- Scales to all screen sizes using Bootstrap’s grid.
- Hero section switches to stacked layout on small screens.

---

## 🚀 How to Run
1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/easy-booking.git
Open index.html in your browser.

No extra dependencies needed — CSS & JS load from CDN.

🔮 Future Enhancements
Backend Integration (Flask/Django/Node.js)

Real-time search & event updates

Payment gateway integration

User & organizer dashboards

Profile pages with reviews
