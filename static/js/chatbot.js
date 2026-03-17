document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    let currentMode = 'standard'; // 'standard' or 'something_else'
    let lastUserQuery = '';
    let welcomedThisPage = false;

    // Menu Definitions
    const MAIN_MENU_OPTIONS = [
        "Login Help",
        "Registration Help",
        "AI Recommendations",
        "Home Remedies",
        "Customer Service",
        "Something Else"
    ];

    /**
     * Toggles the chat input state and placeholder
     * @param {boolean} enabled 
     */
    function setInputState(enabled) {
        chatInput.disabled = !enabled;
        if (enabled) {
            chatInput.placeholder = "Type your message...";
            chatInput.focus();
        } else {
            chatInput.placeholder = "Please select an option below...";
        }
    }

    // Greeting Bubble Logic
    const GREETING_MESSAGES = [
        "Need Help? 👋",
        "Got a Questions? 💬",
        "How can I help you? ✨",
        "Let's chat! 👩‍⚕️"
    ];
    let currentGreetingIndex = 0;
    let greetingInterval;

    const greetingBubble = document.createElement('div');
    greetingBubble.classList.add('chat-greeting-bubble');
    greetingBubble.textContent = GREETING_MESSAGES[0];
    document.querySelector('.chatbot-container').appendChild(greetingBubble);

    const cycleGreeting = () => {
        currentGreetingIndex = (currentGreetingIndex + 1) % GREETING_MESSAGES.length;
        
        // Use a class for cycling to avoid inline style conflicts
        greetingBubble.classList.add('transitioning');
        
        setTimeout(() => {
            greetingBubble.textContent = GREETING_MESSAGES[currentGreetingIndex];
            greetingBubble.classList.remove('transitioning');
        }, 500);
    };

    const showGreeting = () => {
        if (!chatWindow.classList.contains('active')) {
            greetingBubble.classList.add('show');
            chatbotToggle.classList.add('idle');
            if (greetingInterval) clearInterval(greetingInterval);
            greetingInterval = setInterval(cycleGreeting, 5000);
        }
    };

    const hideGreeting = () => {
        greetingBubble.classList.remove('show');
        chatbotToggle.classList.remove('idle');
        if (greetingInterval) clearInterval(greetingInterval);
    };

    // Show greeting after 3 seconds
    setTimeout(showGreeting, 3000);

    // Toggle Chat Window
    chatbotToggle.addEventListener('click', () => {
        const isActive = chatWindow.classList.toggle('active');
        if (isActive) {
            hideGreeting();
            if (!chatInput.disabled) chatInput.focus();
            
            // Trigger welcome message on first open of this page
            if (!welcomedThisPage) {
                setTimeout(() => {
                    addMessage("Hello! I'm your AyuraAI assistant. How can I help you today?", 'bot');
                    welcomedThisPage = true;
                }, 500);
            }
        } else {
            // Re-show greeting after a short delay if closed
            setTimeout(showGreeting, 1000);
        }
    });

    // Close Chat Window
    closeChat.addEventListener('click', () => {
        chatWindow.classList.remove('active');
        setTimeout(showGreeting, 1000);
    });

    // Send Message
    chatForm.addEventListener('submit', async (e) => {
        if (e) e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to UI
        addMessage(message, 'user');
        chatInput.value = '';

        if (currentMode === 'something_else') {
            lastUserQuery = message;
            currentMode = 'standard'; 
            setInputState(false);
            const isLogged = !!document.querySelector('.user-menu');
            const followUpText = isLogged ? 
                "Got it! Since you're logged in, we have your name and email. Please provide your phone number so our team can reach you:" :
                "Got it! Please provide your details so our team can assist you with this query:";
            
            addMessage(followUpText, 'bot');
            renderSupportForm(lastUserQuery);
            return;
        }

        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Remove typing indicator and add bot response
            typingIndicator.remove();
            addMessage(data.response, 'bot');
        } catch (error) {
            console.error('Error:', error);
            if (typingIndicator) typingIndicator.remove();
            addMessage("I'm sorry, I'm having trouble connecting right now. Please try again later.", 'bot');
        }
    });

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        // Handle line breaks in response
        const formattedText = text.replace(/\n/g, '<br>');
        messageDiv.innerHTML = formattedText;
        
        chatMessages.appendChild(messageDiv);

        // Hierarchical Quick Replies
        if (sender === 'bot') {
            const lowerText = text.toLowerCase();
            
            // Default: Lock input unless specially handled
            setInputState(false); 

            // Level 1: Initial/Help or returning to main menu
            if (lowerText.includes("how can i help you today?") || 
                lowerText.includes("please ask a related question.") ||
                lowerText.includes("returning to main menu...")) {
                addQuickReplies(MAIN_MENU_OPTIONS);
            }
            // Level 2: Customer Service sub-options
            else if (lowerText.includes("contact our customer service team?")) {
                addQuickReplies([
                    "In Chat", "Phone Call"
                ]);
            }
            // Special case: "Something Else" prompt
            else if (lowerText.includes("sure! please type your question or concern below.")) {
                setInputState(true); 
            }
            // Transitions to forms
            else if (lowerText.includes("please provide your details so our team can reach you:") ||
                     lowerText.includes("please provide your details so our team can assist you with this query:")) {
                // Input stays locked
            }
            // Universal Follow-up: For any other bot message, add options but stay locked
            else {
                addQuickReplies([
                    "Back to Main Menu",
                    "Something Else"
                ]);
            }
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addQuickReplies(options) {
        const container = document.createElement('div');
        container.classList.add('quick-replies-container');
        
        options.forEach(option => {
            const chip = document.createElement('button');
            chip.classList.add('quick-reply-chip');
            chip.textContent = option;
            chip.addEventListener('click', () => {
                if (option === "Something Else") {
                    currentMode = 'something_else';
                    addMessage("Sure! Please type your question or concern below.", 'bot');
                } else if (option === "Back to Main Menu") {
                    currentMode = 'standard';
                    addMessage("Returning to Main Menu...", 'bot');
                } else if (option === "Phone Call") {
                    currentMode = 'standard';
                    const isLogged = !!document.querySelector('.user-menu');
                    const followUpText = isLogged ? 
                        "Since you're logged in, we have your name and email. Please provide your phone number so our team can reach you:" :
                        "Please provide your details so our team can reach you:";
                    addMessage(followUpText, 'bot');
                    renderSupportForm("Callback Request via Phone Call");
                } else {
                    // Regular option chip
                    currentMode = 'standard';
                    chatInput.value = option;
                    chatInput.disabled = false; 
                    chatForm.dispatchEvent(new Event('submit'));
                }
            });
            container.appendChild(chip);
        });
        
        chatMessages.appendChild(container);
    }

    function renderSupportForm(capturedMessage = "") {
        if (document.querySelector('.support-form')) return;
        setInputState(false); 

        const isLogged = !!document.querySelector('.user-menu');

        const formDiv = document.createElement('div');
        formDiv.classList.add('support-form');
        formDiv.innerHTML = `
            <h4>Your Contact Details</h4>
            ${!isLogged ? `
            <div class="support-field-group">
                <input type="text" id="supp-name" placeholder="Your Name" autocomplete="name">
                <span id="name-error" class="error-msg">Please enter a valid alphabetic name.</span>
            </div>
            <div class="support-field-group">
                <input type="email" id="supp-email" placeholder="Your Email" autocomplete="email">
                <span id="email-error" class="error-msg">Please enter a valid email address.</span>
            </div>
            ` : ''}
            <div class="support-field-group">
                <input type="tel" id="supp-phone" placeholder="10-Digit Phone Number" autocomplete="tel">
                <span id="phone-error" class="error-msg">Please enter a valid 10-digit number.</span>
            </div>
            <button id="supp-submit">Submit Request</button>
        `;
        
        chatMessages.appendChild(formDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const nameInput = document.getElementById('supp-name');
        const emailInput = document.getElementById('supp-email');
        const phoneInput = document.getElementById('supp-phone');
        const submitBtn = document.getElementById('supp-submit');

        const nameRegex = /^[a-zA-Z\s]{2,50}$/;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const phoneRegex = /^[0-9]{10}$/;

        const validateField = (input, regex, errorId) => {
            if (!input) return true; // Field might be hidden if logged in
            const errorSpan = document.getElementById(errorId);
            const isValid = regex.test(input.value.trim());
            if (isValid || input.value.trim() === '') {
                input.classList.remove('invalid');
                errorSpan.classList.remove('active');
                return true;
            } else {
                input.classList.add('invalid');
                errorSpan.classList.add('active');
                return false;
            }
        };

        // Live validation
        if (nameInput) nameInput.addEventListener('input', () => validateField(nameInput, nameRegex, 'name-error'));
        if (emailInput) emailInput.addEventListener('input', () => validateField(emailInput, emailRegex, 'email-error'));
        phoneInput.addEventListener('input', () => validateField(phoneInput, phoneRegex, 'phone-error'));

        submitBtn.addEventListener('click', async () => {
            const isNameValid = !nameInput || (validateField(nameInput, nameRegex, 'name-error') && nameInput.value.trim() !== '');
            const isEmailValid = !emailInput || (validateField(emailInput, emailRegex, 'email-error') && emailInput.value.trim() !== '');
            const isPhoneValid = validateField(phoneInput, phoneRegex, 'phone-error') && phoneInput.value.trim() !== '';

            if (nameInput && !isNameValid) nameInput.classList.add('invalid');
            if (emailInput && !isEmailValid) emailInput.classList.add('invalid');
            if (!isPhoneValid) phoneInput.classList.add('invalid');

            if (!isNameValid || !isEmailValid || !isPhoneValid) return;

            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';

            try {
                const payload = { 
                    phone: phoneInput.value.trim(),
                    message: capturedMessage
                };
                if (nameInput) payload.name = nameInput.value.trim();
                if (emailInput) payload.email = emailInput.value.trim();

                const response = await fetch('/api/support-request', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                
                if (data.success) {
                    formDiv.remove();
                    addMessage(data.message, 'bot');
                } else {
                    alert(data.message || "Something went wrong.");
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit Request';
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Failed to send request. Please try again.");
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Request';
            }
        });
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('typing-indicator');
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicator;
    }

    // Initial greeting bubble logic is handled by setTimeout at top
});
