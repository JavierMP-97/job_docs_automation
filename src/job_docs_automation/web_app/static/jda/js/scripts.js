
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

            newSection.innerHTML = data.content;

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

    function nextStep(event) {
        // Call the backend to get the generated text for the current step
        const dynamicSteps = document.querySelectorAll('.step-block');
        const firstStep = dynamicSteps.length === 1;
        let bodyData = {};
        if (firstStep) {
            bodyData['job_description'] = setJobDescription();
        }
        callBackendForContent(event, '/generate-step/', bodyData);
    }

    function retryStep(event) {
        const dynamicSteps = document.querySelectorAll('.step-block');
        dynamicSteps[dynamicSteps.length - 1].remove();
        let bodyData = {};
        bodyData['retry'] = true;
        callBackendForContent(event, '/generate-step/', bodyData);
    }

    function leftStep(event) {
        const dynamicSteps = document.querySelectorAll('.step-block');
        dynamicSteps[dynamicSteps.length - 1].remove();
        callBackendForContent(event, '/left-step/', {});
    }

    function rightStep(event) {
        const dynamicSteps = document.querySelectorAll('.step-block');
        dynamicSteps[dynamicSteps.length - 1].remove();
        callBackendForContent(event, '/right-step/', {});
    }

    function saveStep(event) {
        fetch('/save-step/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Include CSRF token for POST request
            },
        })
        .then(response => response.json())
        .then(data => {
            // Create a new section dynamically
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('save-message');
            messageDiv.innerHTML = data.success ? 'Success' : 'Error';
            messageDiv.style.color = data.success ? 'green' : 'red';
            dynamicSteps.appendChild(messageDiv);
            if (data.success) {
                alert('Step saved successfully.');
            } else {
                alert('Failed to save step.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        }
        );
    }

    function callBackendForContent(event, endPoint, bodyData){
        // Remove previous buttons and text
        document.querySelectorAll('.action-buttons-next, .action-buttons-line, .next-step-name').forEach(el => el.remove());
        // Show loading animation
        showLoadingAnimation();
        fetch(endPoint, {
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
            console.error('Error:', error);
        });
    }

    const dynamicSteps = document.getElementById('dynamic-steps');

    // Event delegation for dynamically created buttons
    dynamicSteps.addEventListener('click', (event) => {
        if (event.target.matches('.next-btn')) {
            nextStep(event);
        } else if (event.target.matches('.retry-btn')) {
            retryStep(event);
        } else if (event.target.matches('.left-btn')) {
            leftStep(event);
        } else if (event.target.matches('.right-btn')) {
            rightStep(event);
        } else if (event.target.matches('.save-btn')) {
            saveStep(event);
        }
    });

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
