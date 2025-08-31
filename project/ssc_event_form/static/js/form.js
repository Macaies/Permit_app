// Multi-step form with smooth transitions
document.addEventListener("DOMContentLoaded", function () {
  const formSteps = document.querySelectorAll(".form-step");
  const progressSteps = document.querySelectorAll(".progress-step");
  const nextBtns = document.querySelectorAll(".btn-next");
  const prevBtns = document.querySelectorAll(".btn-prev");

  let formStepIndex = 0;

  function updateFormSteps() {
    formSteps.forEach((step, idx) => {
      step.classList.remove("active", "fade-slide");
      if (idx === formStepIndex) {
        step.classList.add("active", "fade-slide");
      }
    });

    progressSteps.forEach((step, idx) => {
      step.classList.toggle("active", idx <= formStepIndex);
    });
  }

  nextBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      if (formStepIndex < formSteps.length - 1) {
        formStepIndex++;
        updateFormSteps();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  });

  prevBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      if (formStepIndex > 0) {
        formStepIndex--;
        updateFormSteps();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  });

  updateFormSteps();
});
