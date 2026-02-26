import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { WorkspaceProvider } from "@/context/WorkspaceContext";
import App from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <WorkspaceProvider>
      <App />
    </WorkspaceProvider>
  </StrictMode>
);
