const form = document.getElementById("edit");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const id = form.elements.id.value;
  const password = form.elements.password.value;
  const text = form.elements.message_content.value;
  if (id === null) {
    return;
  }
  const res = await fetch(`/edit`, {
    method: "post",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id: id,
      text: text,
      password: password,
    }),
  });

  const status = document.getElementById("status");

  status.hidden = false;

  if (res.ok) status.textContent = "Success!";
  else status.textContent = `Failed: ${await res.text()}`;

  form.reset();
});
