//configuration
let API_BASE_URL = '';

//loading posts
async function loadPosts() {
    const apiUrlInput = document.getElementById('api-base-url');
    API_BASE_URL = apiUrlInput.value.trim();

    if (!API_BASE_URL) {
        alert('Please enter an API Base URL');
        return;
    }

    const container = document.getElementById('post-container');
    container.innerHTML = '<div class="loading">Loading posts...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/posts`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const posts = await response.json();
        displayPosts(posts);
    } catch (error) {
        console.error('Error loading posts:', error);
        container.innerHTML = `
            <div class="error">
                 Failed to load posts. Make sure the API is running.<br>
                Error: ${error.message}
            </div>
        `;
    }
}

//displaying posts
function displayPosts(posts) {
    const container = document.getElementById('post-container');

    if (!posts || posts.length === 0) {
        container.innerHTML = '<div class="empty">No posts yet. Add one above!</div>';
        return;
    }

    container.innerHTML = posts.map(post => `
        <div class="post" id="post-${post.id}">
            <h3>${escapeHtml(post.title)}</h3>
            <div class="content">${escapeHtml(post.content)}</div>
            <div class="actions">
                <button class="btn btn-warning" onclick="showEditForm(${post.id})">✏️Edit</button>
                <button class="btn btn-danger" onclick="deletePost(${post.id})">🗑️Delete</button>
            </div>
            <!-- Edit Form (hidden by default) -->
            <div id="edit-form-${post.id}" class="edit-form" style="display:none;">
                <h4>✏️ Edit Post</h4>
                <div class="form-group">
                    <label>Title:</label>
                    <input type="text" id="edit-title-${post.id}" value="${escapeHtml(post.title)}">
                </div>
                <div class="form-group">
                    <label>Content:</label>
                    <textarea id="edit-content-${post.id}" rows="3">${escapeHtml(post.content)}</textarea>
                </div>
                <button class="btn btn-success" onclick="updatePost(${post.id})">💾Save Changes</button>
                <button class="btn btn-secondary" onclick="hideEditForm(${post.id})">␘Cancel</button>
            </div>
        </div>
    `).join('');
}

//adding posts
async function addPost() {
    const apiUrlInput = document.getElementById('api-base-url');
    API_BASE_URL = apiUrlInput.value.trim();

    if (!API_BASE_URL) {
        alert('Please enter an API Base URL');
        return;
    }

    const titleInput = document.getElementById('post-title');
    const contentInput = document.getElementById('post-content');

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();

    if (!title || !content) {
        alert('Please enter both title and content');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/posts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add post');
        }

        // Clear inputs
        titleInput.value = '';
        contentInput.value = '';

        // Reload posts
        await loadPosts();

    } catch (error) {
        console.error('Error adding post:', error);
        alert(`Failed to add post: ${error.message}`);
    }
}

//delete posts
async function deletePost(id) {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    const apiUrlInput = document.getElementById('api-base-url');
    API_BASE_URL = apiUrlInput.value.trim();

    try {
        const response = await fetch(`${API_BASE_URL}/posts/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to delete post');
        }

        await loadPosts();

    } catch (error) {
        console.error('Error deleting post:', error);
        alert(`Failed to delete post: ${error.message}`);
    }
}

//show - edit form
function showEditForm(id) {
    const form = document.getElementById(`edit-form-${id}`);
    if (form) {
        form.style.display = 'block';
    }
}

//hide - edit form
function hideEditForm(id) {
    const form = document.getElementById(`edit-form-${id}`);
    if (form) {
        form.style.display = 'none';
    }
}

//updating post
async function updatePost(id) {
    const apiUrlInput = document.getElementById('api-base-url');
    API_BASE_URL = apiUrlInput.value.trim();

    const titleInput = document.getElementById(`edit-title-${id}`);
    const contentInput = document.getElementById(`edit-content-${id}`);

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();

    if (!title || !content) {
        alert('Please enter both title and content');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/posts/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update post');
        }

        await loadPosts();

    } catch (error) {
        console.error('Error updating post:', error);
        alert(`Failed to update post: ${error.message}`);
    }
}

//utility - escape html
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

//loading post on page load
document.addEventListener('DOMContentLoaded', function() {
    loadPosts();
});