const form = document.getElementById("login");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const password = form.elements.password.value;

  const res = await fetch(`/all`, {
    method: "post",
    redirect: "manual",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      password: password,
    }),
  });
  window.location.replace(res.url);
});
