import React from "react";

function Dashboard() {
  return (
    <div>
      <h1>Welcome to Habit Builder Dashboard</h1>
      <button onClick={() => {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }}>
        Logout
      </button>
    </div>
  );
}

export default Dashboard;
