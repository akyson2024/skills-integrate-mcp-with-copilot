document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const loginButton = document.getElementById("login-button");
  const loginSection = document.getElementById("login-section");
  const logoutButton = document.getElementById("logout-button");
  const teacherInfo = document.getElementById("teacher-info");

  // Check if teacher is logged in
  const teacherData = localStorage.getItem("teacher");
  if (teacherData) {
    const teacher = JSON.parse(teacherData);
    showTeacherInfo(teacher);
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("teacher-email").value;
    const password = document.getElementById("teacher-password").value;

    try {
      const response = await fetch(`/auth/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
        method: "POST"
      });

      const result = await response.json();

      if (response.ok) {
        const teacher = result.teacher;
        localStorage.setItem("teacher", JSON.stringify(teacher));
        showTeacherInfo(teacher);
        loginForm.reset();
      } else {
        alert(result.detail || "Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert("Login failed. Please try again.");
    }
  });

  logoutButton.addEventListener("click", () => {
    localStorage.removeItem("teacher");
    showLoginForm();
  });

  function showTeacherInfo(teacher) {
    loginSection.classList.add("hidden");
    teacherInfo.classList.remove("hidden");
    teacherInfo.querySelector(".teacher-name").textContent = teacher.name;
    teacherInfo.querySelector(".teacher-email").textContent = teacher.email;
    document.body.classList.add("teacher-mode");
  }

  function showLoginForm() {
    loginSection.classList.remove("hidden");
    teacherInfo.classList.add("hidden");
    document.body.classList.remove("teacher-mode");
  }
});