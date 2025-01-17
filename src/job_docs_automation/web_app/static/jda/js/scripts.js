
document.addEventListener('DOMContentLoaded', () => {

    function createDynamicSection(data) {
        hideLoadingAnimation();
        if (data.content) {
            // Remove previous buttons and text
            document.querySelectorAll('.action-buttons-next, .action-buttons-line, .next-step-name').forEach(el => el.remove());

            // Create a new section dynamically
            const dynamicSteps = document.getElementById('dynamic-steps');
            const newSection = document.createElement('section');
            newSection.classList.add('step-block');

            newSection.innerHTML = `
                <h2 class="step-title">${data.prev_step}</h2>
                <div class="step-content">
                    ${data.content} <!-- Dynamic content goes here -->
                </div>
                <div class="action-buttons-line">
                    <button class="btn left-btn">Left</button>
                    <button class="btn retry-btn">Retry</button>
                    <button class="btn right-btn">Right</button>
                </div>
            `;

            // Check if next_step is in data
            if (data.next_step) {
                newSection.innerHTML += `
                    <h2 class="next-step-name">${data.next_step}</h2>
                    <div class="action-buttons-next">
                        <button class="btn next-btn">Next</button>
                    </div>
                `;
            }

            dynamicSteps.appendChild(newSection);
        } else {
            showErrorMessage();
            alert('Failed to generate content.');
        }
    };

    function showLoadingAnimation() {
        const loadingAnimation = document.createElement('div');
        loadingAnimation.classList.add('loading-animation');
        loadingAnimation.innerHTML = 'Loading...';
        // Append to last step-block found in the whole document
        const stepBlocks = document.querySelectorAll('.step-block');
        stepBlocks[stepBlocks.length - 1].appendChild(loadingAnimation);
    }

    function hideLoadingAnimation() {
        const loadingAnimation = document.querySelector('.loading-animation');
        if (loadingAnimation) {
            loadingAnimation.remove();
        }
    }

    function showErrorMessage() {
        const dynamicSteps = document.getElementById('dynamic-steps');
        const errorMessage = document.createElement('div');
        errorMessage.classList.add('error-message');
        errorMessage.innerHTML = 'Failed to load content. Please try again.';
        dynamicSteps.appendChild(errorMessage);
    }

    function setJobDescription() {
        job_description_elem = document.getElementById('job-description');
        job_description = job_description_elem.value;
        // Change job_description_elem to a div element
        job_description_elem.outerHTML = `<div id="job-description" class="step-content">${job_description}</div>`;
        return job_description;
    }

    function nextButtonFunc(event, retry=false) {
        // Remove previous buttons and text
        document.querySelectorAll('.action-buttons-next, .action-buttons-line, .next-step-name').forEach(el => el.remove());
        // Show loading animation
        showLoadingAnimation();
        // Call the backend to get the generated text for the current step
        const dynamicSteps = document.querySelectorAll('.step-block');
        const firstStep = dynamicSteps.length === 1;
        let bodyData = {};
        if (firstStep) {
            bodyData['job_description'] = setJobDescription();
        }
        if (retry) {
            dynamicSteps[dynamicSteps.length - 1].remove();
            bodyData['retry'] = true;
        }
        fetch('/next-step/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Include CSRF token for POST request
            },
            body: JSON.stringify(bodyData)
        })
        .then(response => response.json())
        .then(data => createDynamicSection(data))
        .catch(error => {
            hideLoadingAnimation();
            showErrorMessage();
            console.error('Error:', error)
        });
    };

    const dynamicSteps = document.getElementById('dynamic-steps');

    // Event delegation for dynamically created buttons
    dynamicSteps.addEventListener('click', (event) => {
        if (event.target.matches('.next-btn')) {
            nextButtonFunc(event);
        } else if (event.target.matches('.retry-btn')) {
            nextButtonFunc(event, retry=true);
        } else if (event.target.matches('.left-btn')) {
            alert('Left button clicked!');
        } else if (event.target.matches('.right-btn')) {
            alert('Right button clicked!');
        }
    });

    // Event listener for the next button
    document.getElementById("first-step").addEventListener('click', nextButtonFunc);

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
