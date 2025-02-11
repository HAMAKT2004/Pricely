let menu = document.querySelector('#menu-icon');
let navlist = document.querySelector('.navlist');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
}

window.onscroll = () => {
    menu.classList.remove('bx-x');
    navlist.classList.remove('open');
}



/* Offers Sliding Panel Starts */
let currentIndex = 0;
let banners = [];
let dots = [];
let isTransitioning = false;

// Load the scraped data from offers.json
fetch('offer.json')
    .then(response => response.json())
    .then(data => {
        banners = data;
        const bannerContainer = document.getElementById('bannerContainer');
        const dotsContainer = document.getElementById('dotsContainer');

        // Create and append banner cards with clickable links
        banners.forEach((offer, index) => {
            const bannerCard = document.createElement('div');
            bannerCard.classList.add('banner-card');

            const anchor = document.createElement('a');
            anchor.href = offer["Product Link"];
            anchor.target = "_blank";  // Open link in new tab

            const img = document.createElement('img');
            img.src = offer["Image Source"];
            img.alt = offer["Alt Text"];

            // Error handling for broken images
            img.onerror = function() {
                this.src = 'path/to/your/default-placeholder-image.jpg';
            };

            anchor.appendChild(img);
            bannerCard.appendChild(anchor);
            bannerContainer.appendChild(bannerCard);

            // Create dots
            const dot = document.createElement('span');
            dot.classList.add('dot');
            dot.addEventListener('click', () => goToSlide(index));  // Add click event to navigate
            dotsContainer.appendChild(dot);
            dots.push(dot);  // Store the dot for future reference
        });

        // Clone the first slide and append it to the end to handle looping
        const firstClone = bannerContainer.firstElementChild.cloneNode(true);
        bannerContainer.appendChild(firstClone);

        // Set the first dot to be active
        dots[0].classList.add('active');

        // Start the slideshow
        setInterval(nextSlide, 5000);
    })
    .catch(error => console.error('Error loading the offer banners:', error));

// Function to show the next slide
function nextSlide() {
    if (isTransitioning) return;
    isTransitioning = true;

    currentIndex++;
    updateBannerPosition();

    // Detect when the slider reaches the last (cloned) slide
    if (currentIndex === banners.length) {
        setTimeout(() => {
            // Jump back to the first slide without a transition
            bannerContainer.style.transition = 'none';
            currentIndex = 0;
            updateBannerPosition();

            // Re-enable the transition after the jump
            setTimeout(() => {
                bannerContainer.style.transition = 'transform 0.7s ease';
                isTransitioning = false;
            }, 20); // A tiny delay to ensure the jump completes before transition resumes
        }, 700); // Matches the transition duration to ensure the user doesn't see the jump
    } else {
        setTimeout(() => isTransitioning = false, 700); // Matches the transition duration
    }
}

// Function to show the previous slide
function prevSlide() {
    if (isTransitioning) return;
    isTransitioning = true;

    currentIndex--;
    if (currentIndex < 0) {
        // Jump to the last real slide without a transition
        bannerContainer.style.transition = 'none';
        currentIndex = banners.length - 1;
        updateBannerPosition();

        // Re-enable transition after jump
        setTimeout(() => {
            bannerContainer.style.transition = 'transform 0.7s ease';
            isTransitioning = false;
        }, 20);
    } else {
        updateBannerPosition();
        setTimeout(() => isTransitioning = false, 700);
    }
}

// Function to update the banner position
function updateBannerPosition() {
    const bannerContainer = document.getElementById('bannerContainer');
    bannerContainer.style.transform = `translateX(-${currentIndex * 100}%)`;

    // Update the active dot (excluding the cloned slide)
    dots.forEach(dot => dot.classList.remove('active'));
    if (currentIndex < banners.length) {
        dots[currentIndex].classList.add('active');
    }
}

// Function to go to a specific slide
function goToSlide(index) {
    if (isTransitioning) return;
    currentIndex = index;
    updateBannerPosition();
}

// Event listeners for navigation buttons
document.getElementById('nextArrow').addEventListener('click', nextSlide);
document.getElementById('prevArrow').addEventListener('click', prevSlide);


/* Offers Sliding Panel Ends */


// news
const apiKey = '11c9015e1471424b9b641b9b8364b424'; // Replace with your API key
const url = `https://newsapi.org/v2/everything?q=smartphone&apiKey=${apiKey}`;

let displayedArticles = new Set(); // To track displayed articles

function fetchSmartphoneNews() {
  fetch(url)
    .then(response => response.json())
    .then(data => {
      const articles = data.articles.filter(article => 
        !displayedArticles.has(article.title) && // Avoid duplicates
        article.title.toLowerCase().includes('smartphone') // Filter for smartphone-related articles
      ).slice(0, 8); // Get top 8 articles

      // Mark articles as displayed
      articles.forEach(article => displayedArticles.add(article.title));

      displayNews(articles);
    })
    .catch(error => console.error('Error fetching smartphone news:', error));
}

function displayNews(articles) {
  const newsContainer = document.getElementById('news-container');

  // Clear existing news before displaying new ones
  newsContainer.innerHTML = '';

  articles.forEach(article => {
    const newsItem = document.createElement('div');
    newsItem.innerHTML = `
  <a href="${article.url}" target="_blank" style="text-decoration: none; color: inherit;">
    <h3>${article.title}</h3>
    <img src="${article.urlToImage}" alt="News image" />
    <p>${article.description}</p>
  </a>
`;

    newsContainer.appendChild(newsItem);
  });
}

// Fetch the news initially
fetchSmartphoneNews();

// Refresh the news every minute
setInterval(fetchSmartphoneNews, 60000); // 60000 ms = 1 minute


const menuButton = document.getElementById('menu-button');
const closeButton = document.getElementById('close-button');
const sideDrawer = document.getElementById('side-drawer');
const overlay = document.getElementById('overlay');

// Function to open the side drawer
menuButton.addEventListener('click', () => {
    sideDrawer.style.width = '250px';
    overlay.classList.add('open');
});

// Function to close the side drawer
closeButton.addEventListener('click', () => {
    sideDrawer.style.width = '0';
    overlay.classList.remove('open');
});

// Also close when clicking the overlay
overlay.addEventListener('click', () => {
    sideDrawer.style.width = '0';
    overlay.classList.remove('open');
});



  
  