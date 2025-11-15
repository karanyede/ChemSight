import { ChangeEvent, FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, register } from "../services/api";
import { setToken } from "../utils/auth";

const LoginForm = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const toggleMode = () => {
    setMode((prevMode: "login" | "register") =>
      prevMode === "login" ? "register" : "login"
    );
    setError(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response =
        mode === "login"
          ? await login(username, password)
          : await register(username, password, email);
      setToken(response.token);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError("Authentication failed. Please check your details.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section aria-labelledby="auth-heading" className="auth-container">
      <h1 id="auth-heading">
        {mode === "login" ? "Sign in" : "Create an account"}
      </h1>
      <form onSubmit={handleSubmit} className="auth-form">
        <div>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            autoComplete="username"
            value={username}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              setUsername(event.target.value)
            }
            required
          />
        </div>
        {mode === "register" && (
          <div>
            <label htmlFor="email">Email (optional)</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event: ChangeEvent<HTMLInputElement>) =>
                setEmail(event.target.value)
              }
              placeholder="you@example.com"
            />
          </div>
        )}
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete={
              mode === "login" ? "current-password" : "new-password"
            }
            value={password}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              setPassword(event.target.value)
            }
            required
            minLength={8}
          />
        </div>
        {error && <p role="alert">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting
            ? "Please wait…"
            : mode === "login"
            ? "Log in"
            : "Register"}
        </button>
      </form>
      <button type="button" className="toggle" onClick={toggleMode}>
        {mode === "login"
          ? "Need an account? Register"
          : "Already have an account? Sign in"}
      </button>
    </section>
  );
};

export default LoginForm;
