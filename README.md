# Booking System Application

This is a Django-based web application for managing bookings of cylinder stock. It allows users to book cylinders, manage deliveries, generate invoices, and view booking history.

## Features

- **User Authentication**: Users can sign up, log in, and log out securely.
- **Booking Management**: Users can book cylinders by specifying cylinder type and preferred delivery date.
- **Delivery Management**: Admin can assign delivery personnel to bookings and track deliveries.
- **Invoice Generation**: Admin can generate invoices for successful payments.
- **Reporting**: Admin can generate reports on bookings.
- **Email/SMS Notifications**: Users receive notifications on booking status updates.
- **Payment Integration**: Integrated with Stripe for secure payment processing.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/davideke1/simple_booking_application.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    - Copy the `.env.example` file to `.env` and fill in the required environment variables such as `SECRET_KEY`, `STRIPE_SECRET_KEY`, etc.

4. Run migrations:

    ```bash
    python manage.py migrate
    ```

5. Create a superuser:

    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Usage

- Visit the admin panel at `http://localhost:8000/admin` or `http://localhost:8000/admin-view\dashboard`(admin@admin.com) to manage users, bookings, deliveries, etc.
- Users can access the booking system frontend to book cylinders and view booking history.
- Admin can generate invoices and view reports from the admin panel.

## Contributing

Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
