import { Link, useLocation, useNavigate } from "react-router-dom";
import { clearToken, isAuthenticated } from "../utils/auth";
import "./NavBar.css";

const NavBar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearToken();
    navigate("/login", { replace: true });
  };

  const links = [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/upload", label: "Upload" },
    { to: "/history", label: "History" },
  ];

  return (
    <header className="app-header">
      <nav aria-label="Primary">
        <Link className="brand" to="/dashboard">
          Chemical Visualizer
        </Link>
        <ul className="nav-links">
          {links.map((link) => (
            <li key={link.to}>
              <Link
                to={link.to}
                className={
                  location.pathname.startsWith(link.to) ? "active" : ""
                }
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
        {isAuthenticated() && (
          <button
            type="button"
            className="logout"
            onClick={handleLogout}
            aria-label="Log out"
          >
            Logout
          </button>
        )}
      </nav>
    </header>
  );
};

export default NavBar;
