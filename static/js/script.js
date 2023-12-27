let navbar = document.querySelector('.navbar')

document.querySelector('#menu-bar').onclick = () =>{
    navbar.classList.toggle('active');
}


document.querySelector('#close').onclick = () =>{
    navbar.classList.remove('active');
}


window.onscroll = () =>{

    navbar.classList.remove('active');
    sortBar.classList.remove('active');

    if(window.scrollY > 100){
        document.querySelector('header').classList.add('active');
    }else{
        document.querySelector('header').classList.remove('active');
    }

}




function validateForm() {
    var cardNumber = document.getElementById('cardNumber').value;
    var expiryDate = document.getElementById('expiryDate').value;
    var cvv = document.getElementById('cvv').value;
    var email = document.getElementById('email').value;
  
    // Validate card number (must be 16 digits)
    var expiryRegex = /^((0[1-9])|(1[0-2]))\/(\d{2})$/;
    if (cardNumber.length !== 16) {
      alert('Please enter a valid 16-digit card number.');
      return false;
    }
  
    // Validate expiry date (must be in the format MM/YY)
    var expiryRegex = /^((0[1-9])|(1[0-2]))\/(\d{2})$/;
    if (!expiryRegex.test(expiryDate)) {
      alert('Please enter a valid expiry date in the format MM/YY.');
      return false;
    }
  
    // Validate CVV (must be 3 digits)
    if (cvv.length !== 3) {
      alert('Please enter a valid 3-digit CVV.');
      return false;
    }
  
    // Validate email (must be a valid email address)
    var emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(email)) {
      alert('Please enter a valid email address.');
      return false;
    }
  
     // If form validation passes, redirect to the specified route
     if (validationsPass) {
        return true;  // Allow default form submission
      }
    
      return false; 
  }
  