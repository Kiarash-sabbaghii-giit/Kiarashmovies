document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const suggestionsBox = document.getElementById('suggestions');
    let timer;

    searchInput.addEventListener('input', function () {
        clearTimeout(timer);
        const q = this.value.trim();
        if (q.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }
        timer = setTimeout(() => {
            fetch(`/search/suggestions/?q=${encodeURIComponent(q)}`)
                .then(r => r.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    if (data.length) {
                        data.forEach(item => {
                            const li = document.createElement('li');
                            const a = document.createElement('a');
                            a.href = `/movie/${item.imdb_code}/`;
                            a.innerHTML = `
                                <span class="suggestion-title">${item.title}</span>
                                <span>
                                    <span class="suggestion-year">${item.year}</span>
                                    <span class="suggestion-rate">${item.rate}</span>
                                </span>
                            `;
                            li.appendChild(a);
                            suggestionsBox.appendChild(li);
                        });
                        suggestionsBox.style.display = 'block';
                    } else {
                        suggestionsBox.style.display = 'none';
                    }
                })
                .catch(e => console.error(e));
        }, 300);
    });

    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
});