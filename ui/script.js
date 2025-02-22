// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const targetSection = document.querySelector(targetId);
      if (targetSection) {
        targetSection.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Toggle Chatbot
  const chatbotToggle = document.getElementById('chatbot-toggle');
  const chatbot = document.getElementById('chatbot');
  const chatbotClose = document.getElementById('chatbot-close');
  
  chatbotToggle.addEventListener('click', () => {
    if (chatbot.style.display === 'block') {
      chatbot.style.animation = 'slide-down 0.3s ease-out';
      setTimeout(() => {
        chatbot.style.display = 'none';
      }, 300);
    } else {
      chatbot.style.display = 'block';
      chatbot.style.animation = 'slide-up 0.3s ease-out';
    }
  });
  
  chatbotClose.addEventListener('click', () => {
    chatbot.style.animation = 'slide-down 0.3s ease-out';
    setTimeout(() => {
      chatbot.style.display = 'none';
    }, 300);
  });