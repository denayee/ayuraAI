fetch("https://ayuraai-1.onrender.com/predict", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(userData)
})
.then(res => res.json())
.then(data => {
  console.log(data);
});