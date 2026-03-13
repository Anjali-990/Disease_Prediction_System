// OPEN MODAL
function openModal(id) {
  var modal = new bootstrap.Modal(document.getElementById(id));
  modal.show();
}

// CLOSE ONE MODAL & OPEN ANOTHER
function switchModal(oldId, newId) {
  var oldModal = bootstrap.Modal.getInstance(document.getElementById(oldId));
  oldModal.hide();

  setTimeout(() => {
    var newModal = new bootstrap.Modal(document.getElementById(newId));
    newModal.show();
  }, 300);
}

document.addEventListener("DOMContentLoaded", function () {
  // Open modal if Django sent flags
  if (window.openLogin === true) {
    openModal("loginModal");
  }

  if (window.openSignup === true) {
    openModal("signupModal");
  }
});
