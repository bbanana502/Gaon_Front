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

    editBtn.addEventListener('click', () => {
        isEditing = !isEditing;

        if (isEditing) {
            // Enable inputs
            inputs.forEach(input => input.disabled = false);
            editBtn.textContent = 'Save';
            editBtn.style.backgroundColor = '#2ecc71'; // Green for save
            
            // Visual cue for avatar
            profileAvatar.style.cursor = 'pointer';
            profileAvatar.style.border = '2px dashed #4a90e2';
        } else {
            // Disable inputs (Save action)
            inputs.forEach(input => input.disabled = true);
            editBtn.textContent = 'Edit';
            editBtn.style.backgroundColor = ''; // Revert to original color (CSS)
            
            // Remove visual cue
            profileAvatar.style.cursor = 'default';
            profileAvatar.style.border = '1px solid #ddd';

            // Mock Save Alert
            alert('Profile updated successfully!');
        }
    });

    changeEmailBtn.addEventListener('click', () => {
        const newEmail = prompt("Enter new email address:");
        if (newEmail) {
            document.querySelector('.email-addr').textContent = newEmail;
            alert('Email address updated!');
        }
    });
});
