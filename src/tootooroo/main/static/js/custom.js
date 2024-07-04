// static/js/custom.js

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-btn').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const tootId = this.getAttribute('data-toot-id');
            const url = `/toot/${tootId}/like/`;
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                const icon = this.querySelector('i');
                const countSpan = this.querySelector('.like-count');
                if (data.liked) {
                    icon.classList.remove('fa-regular');
                    icon.classList.add('fa-solid');
                } else {
                    icon.classList.remove('fa-solid');
                    icon.classList.add('fa-regular');
                }
                countSpan.textContent = data.like_count;
            });
        });
    });
});
