document.addEventListener('DOMContentLoaded', () => {
    const editBtn = document.getElementById('editBtn');
    const inputs = [
        document.getElementById('nicknameInput'),
        document.getElementById('genderSelect'),
        document.getElementById('languageSelect')
    ];
    const changeEmailBtn = document.getElementById('changeEmailBtn');
    
    // Profile Pic Logic
    const profileAvatar = document.getElementById('profileAvatar');
    const profilePicInput = document.getElementById('profilePicInput');
    const headerProfilePic = document.querySelector('.header-profile-pic'); // To update header too

    let isEditing = false;

    // Trigger file input when avatar is clicked (only if editing)
    profileAvatar.addEventListener('click', () => {
        if (isEditing) {
            profilePicInput.click();
        }
    });

    // Handle file selection
    profilePicInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const imageUrl = `url('${e.target.result}')`;
                profileAvatar.style.backgroundImage = imageUrl;
                headerProfilePic.style.backgroundImage = imageUrl;
            };
            reader.readAsDataURL(file);
        }
    });

    // --- Nickname Initialization ---
    const nicknameDisplay = document.querySelector('.user-info-display h2');
    const nicknameInput = document.getElementById('nicknameInput');
    
    // Load from API
    fetch('/user/me')
        .then(res => res.json())
        .then(data => {
            const storedId = localStorage.getItem('student_id');
            // Prefer API nickname, fallback to stored ID, then default
            const displayName = data.nickname || storedId || 'Student';
            
            nicknameDisplay.textContent = displayName;
            nicknameInput.value = displayName;
        })
        .catch(err => console.error(err));

    // --- Edit Logic ---
    editBtn.addEventListener('click', () => {
        isEditing = !isEditing;

        if (isEditing) {
            // Enable inputs
            inputs.forEach(input => input.disabled = false);
            editBtn.textContent = '저장'; // Changed to Korean "Save"
            editBtn.style.backgroundColor = '#2ecc71'; // Green
            
            // Visual cue for avatar
            profileAvatar.style.cursor = 'pointer';
            profileAvatar.style.border = '2px dashed #4a90e2';
        } else {
            // Disable inputs (Save action)
            inputs.forEach(input => input.disabled = true);
            editBtn.textContent = '수정'; // Changed to Korean "Edit"
            editBtn.style.backgroundColor = ''; 
            
            // Save logic to API
            const newNickname = nicknameInput.value.trim();
            
            fetch('/user/config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nickname: newNickname })
            })
            .then(res => res.json())
            .then(data => {
                nicknameDisplay.textContent = data.nickname;
                alert('프로필이 저장되었습니다!'); 
            })
            .catch(err => {
                alert('저장 실패!');
                console.error(err);
            });

            // Remove visual cue
            profileAvatar.style.cursor = 'default';
            profileAvatar.style.border = '1px solid #ddd';
        }
    });

    changeEmailBtn.addEventListener('click', () => {
        const newEmail = prompt("Enter new email address:");
        if (newEmail) {
            document.querySelector('.email-addr').textContent = newEmail;
            alert('Email address updated!');
        }
    });
    // Logout Logic
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
             if(confirm('로그아웃 하시겠습니까?')) {
                localStorage.removeItem('isLoggedIn');
                localStorage.removeItem('student_id');
                window.location.href = '/';
             }
        });
    }
});
