import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import NavBar from "../components/NavBar";

describe("NavBar", () => {
  test("renders brand and links", () => {
    render(
      <MemoryRouter>
        <NavBar />
      </MemoryRouter>
    );

    const brand = screen.getByText(/chemical visualizer/i);
    expect(brand).toBeInTheDocument();

    const dashboardLink = screen.getByText(/dashboard/i);
    expect(dashboardLink).toBeInTheDocument();
  });
});
