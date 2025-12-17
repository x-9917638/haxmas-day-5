const form = document.getElementById("form");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const password = form.elements.password.value;
  const text = form.elements.message_content.value;
  const author = form.elements.author.value;

  const res = await fetch(`/submit`, {
    method: "post",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: text,
      password: password,
      author: author,
    }),
  });

  const status = document.getElementById("status");

  status.hidden = false;

  if (res.ok) {
    status.textContent = `Success ${await res.text()}`;
  } else status.textContent = `Failed: Error ${await res.text()}`;
});

const status = document.getElementById("status");
status.addEventListener("click", async (event) => {
  event.preventDefault();
  // Success {\n  "id": "uuid"\n}\n'
  const data = JSON.parse(status.textContent.trim().slice(8));
  const id = data.id;
  await navigator.clipboard.writeText(id);
  status.textContent = "ID Copied!";
});
