import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import { Link } from "react-router-dom";

const AppNavbar = () => {
  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="shadow-sm px-3">
      <Container fluid>
        {/* Brand */}
        <Navbar.Brand as={Link} to="/" className="fw-semibold text-uppercase">
          Food Inventory
        </Navbar.Brand>

        {/* Mobile Toggle */}
        <Navbar.Toggle aria-controls="main-navbar" />

        {/* Links */}
        <Navbar.Collapse id="main-navbar">
          <Nav className="ms-auto gap-3">
            <Nav.Link as={Link} to="/">Home</Nav.Link>
            <Nav.Link as={Link} to="/food">Food</Nav.Link>
            <Nav.Link as={Link} to="/other">Other Items</Nav.Link>
            <Nav.Link as={Link} to="/profile">Profile</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;
