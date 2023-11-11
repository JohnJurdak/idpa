// Handle the Search Form submission
document.getElementById('searchForm').onsubmit = function(event) {
    event.preventDefault();
    let word = this.word.value;
    fetchResults('/search', { word: word });
};

// Handle the KNN Form submission
document.getElementById('knnForm').onsubmit = function(event) {
    event.preventDefault();
    let vector = this.vector.value;
    fetchResults('/knn_search', { vector: vector });
};

// Handle the Upload Form submission
document.getElementById('uploadForm').onsubmit = function(event) {
    event.preventDefault();
    let formData = new FormData(this);
    fetchResults('/upload_and_compare', formData);
};

// General function to fetch and display results
function fetchResults(url, body) {
    // Determine if we are sending FormData (for file uploads) or a simple object
    const options = {
        method: 'POST',
        body: body instanceof FormData ? body : new URLSearchParams(body),
    };
    // If the body is not FormData, set the header as 'application/x-www-form-urlencoded'
    if (!(body instanceof FormData)) {
        options.headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
    }

    fetch(url, options)
    .then(response => response.json())
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to display results

// ... other functions remain the same

// Function to display results
function truncateTitle(title) {
    const words = title.split(' ');
    if (words.length > 10) {
        return words.slice(0, 10).join(' ') + '...';
    } else {
        return title;
    }
}

function displayResults(data) {
    let resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<h2>Results</h2>';
    data.forEach(result => {
        let truncatedTitle = truncateTitle(result._source.title);
        let resultDiv = document.createElement('div');
        resultDiv.className = 'result-item';
        resultDiv.innerHTML = `
            <div class="result-image">
            <img src="/static/images/book-image.png" alt="Book Image" />
            </div>
            <div class="result-summary">
                <h3>${truncatedTitle}</h3>
                <button class="details-btn"><i class="fas fa-info-circle"></i></button>
            </div>
        `;

        // Attach event listener for the More Info button
        resultDiv.querySelector('.details-btn').addEventListener('click', function() {
            // Ensure previous modals are removed
            let existingModal = document.querySelector('.modal');
            if (existingModal) {
                existingModal.parentNode.removeChild(existingModal);
            }

            let modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h3>${result._source.title}</h3>
                    <p>ID: ${result._id}</p>
                    <p>Category: ${result._source.category}</p>
                    <p>Description: ${result._source.description}</p>
                    <p>Price: ${result._source.price}</p>
                    <p>Price excl. tax: ${result._source.price_excl_tax}</p>
                    <p>Stars: ${result._source.stars}</p>
                    <p>UPC: ${result._source.upc}</p>
                    <a href="${result._source.url}" target="_blank">Product Page</a>
                </div>
            `;
            document.body.appendChild(modal);
            modal.style.display = 'block';

            // Close Modal
            modal.querySelector('.close').onclick = function() {
                modal.style.display = 'none';
                document.body.removeChild(modal);
            };

            // Close Modal when clicking outside of it
            window.onclick = function(event) {
                if (event.target === modal) {
                    modal.style.display = 'none';
                    document.body.removeChild(modal);
                }
            };
        });

        resultsDiv.appendChild(resultDiv);
    });
}

