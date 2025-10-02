import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import { Link } from "react-router-dom";

const AppNavbar = ({ children }) => {
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
            <Nav.Link as={Link} to="/all_food">Food</Nav.Link>
            <Nav.Link as={Link} to="/other">Other Items</Nav.Link>
            <Nav.Link as={Link} to="/profile">Profile</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;

/*
import { Container, Navbar } from "react-bootstrap";
import { Link, Outlet } from "react-router-dom";

function Main({ children }) {
  return (
    <div>
      <Navbar bg="dark" variant="dark" className="p-3">
        <Link to="/">
          <Navbar.Brand href="#">The Great Project</Navbar.Brand>
        </Link>
      </Navbar>
      <Container fluid className="mt-4">
        <Outlet />
      </Container>
    </div>
  );
}

export default Main;
*/