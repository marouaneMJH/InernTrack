/**
 * CV Generator JavaScript
 * Handles profile management, document generation, and UI interactions
 * 
 * Author: El Moujahid Marouane
 * Version: 1.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // State
    let profile = null;
    let currentModal = null;
    let editingItem = null;

    // DOM Elements
    const tabs = document.querySelectorAll('.cv-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const itemModal = document.getElementById('itemModal');
    const modalForm = document.getElementById('modalForm');
    const modalTitle = document.getElementById('modalTitle');
    const modalFormContent = document.getElementById('modalFormContent');

    // Initialize
    init();

    function init() {
        setupTabs();
        setupModals();
        setupForms();
        loadProfile();
        loadDocuments();
    }

    // =====================
    // Tab Navigation
    // =====================
    
    function setupTabs() {
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.dataset.tab;
                
                // Update tab styles
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show corresponding content
                tabContents.forEach(content => {
                    content.classList.add('hidden');
                });
                document.getElementById(`tab-${tabId}`).classList.remove('hidden');
            });
        });
    }

    // =====================
    // Modal Management
    // =====================
    
    function setupModals() {
        document.getElementById('closeModalBtn').addEventListener('click', closeModal);
        document.getElementById('cancelModalBtn').addEventListener('click', closeModal);
        
        // Close on outside click
        itemModal.addEventListener('click', (e) => {
            if (e.target === itemModal) closeModal();
        });

        // Add buttons
        document.getElementById('addSkillBtn').addEventListener('click', () => openSkillModal());
        document.getElementById('addProjectBtn').addEventListener('click', () => openProjectModal());
        document.getElementById('addEducationBtn').addEventListener('click', () => openEducationModal());
        document.getElementById('addExperienceBtn').addEventListener('click', () => openExperienceModal());
    }

    function openModal(title, formHtml, type, item = null) {
        modalTitle.textContent = title;
        modalFormContent.innerHTML = formHtml;
        currentModal = type;
        editingItem = item;
        itemModal.classList.remove('hidden');
    }

    function closeModal() {
        itemModal.classList.add('hidden');
        modalForm.reset();
        currentModal = null;
        editingItem = null;
    }

    // =====================
    // Forms Setup
    // =====================
    
    function setupForms() {
        // Personal Info Form
        document.getElementById('personalInfoForm').addEventListener('submit', handlePersonalInfoSubmit);
        
        // Modal Form
        modalForm.addEventListener('submit', handleModalSubmit);
        
        // Generate Form
        document.getElementById('generateForm').addEventListener('submit', handleGenerate);
        document.getElementById('analyzeMatchBtn').addEventListener('click', handleAnalyzeMatch);
        
        // Refresh Documents
        document.getElementById('refreshDocsBtn').addEventListener('click', loadDocuments);
    }

    // =====================
    // Profile Loading
    // =====================
    
    async function loadProfile() {
        try {
            const response = await fetch('/api/cv/profile');
            const data = await response.json();
            
            if (data.success && data.profile) {
                profile = data.profile;
                populatePersonalInfo(profile.personal_info);
                renderSkills(profile.skills);
                renderProjects(profile.projects);
                renderEducation(profile.education);
                renderExperience(profile.experience);
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            showToast('Failed to load profile', 'error');
        }
    }

    function populatePersonalInfo(info) {
        if (!info) return;
        document.getElementById('full_name').value = info.full_name || '';
        document.getElementById('email').value = info.email || '';
        document.getElementById('phone').value = info.phone || '';
        document.getElementById('location').value = info.location || '';
        document.getElementById('linkedin').value = info.linkedin || '';
        document.getElementById('github').value = info.github || '';
        document.getElementById('website').value = info.website || '';
        document.getElementById('summary').value = info.summary || '';
    }

    // =====================
    // Personal Info
    // =====================
    
    async function handlePersonalInfoSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await fetch('/api/cv/profile/personal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            
            const result = await response.json();
            if (result.success || response.ok) {
                showToast('Personal information saved!', 'success');
                loadProfile();
            } else {
                showToast(result.error || 'Failed to save', 'error');
            }
        } catch (error) {
            console.error('Error saving personal info:', error);
            showToast('Failed to save personal information', 'error');
        }
    }

    // =====================
    // Skills
    // =====================
    
    function renderSkills(skills) {
        const container = document.getElementById('skillsList');
        const noSkills = document.getElementById('noSkills');
        
        if (!skills || skills.length === 0) {
            container.innerHTML = '';
            noSkills.classList.remove('hidden');
            return;
        }
        
        noSkills.classList.add('hidden');
        container.innerHTML = skills.map(skill => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg" data-skill-id="${skill.id}">
                <div class="flex items-center gap-3">
                    <span class="px-2 py-1 text-xs rounded bg-emerald-100 text-emerald-700">${skill.category}</span>
                    <span class="font-medium">${escapeHtml(skill.name)}</span>
                    <span class="text-sm text-gray-500">${skill.proficiency}</span>
                    ${skill.years_experience ? `<span class="text-sm text-gray-400">(${skill.years_experience} yrs)</span>` : ''}
                </div>
                <div class="flex gap-2">
                    <button type="button" class="text-gray-400 hover:text-blue-500 edit-skill" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="text-gray-400 hover:text-red-500 delete-skill" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
        // Add event listeners
        container.querySelectorAll('.edit-skill').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const skillId = e.target.closest('[data-skill-id]').dataset.skillId;
                const skill = skills.find(s => s.id == skillId);
                openSkillModal(skill);
            });
        });
        
        container.querySelectorAll('.delete-skill').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const skillId = e.target.closest('[data-skill-id]').dataset.skillId;
                if (confirm('Delete this skill?')) {
                    await deleteItem('skills', skillId);
                }
            });
        });
    }

    function openSkillModal(skill = null) {
        const html = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Skill Name *</label>
                    <input type="text" name="name" required value="${skill?.name || ''}"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                        placeholder="Python">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
                    <select name="category" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                        <option value="programming" ${skill?.category === 'programming' ? 'selected' : ''}>Programming</option>
                        <option value="framework" ${skill?.category === 'framework' ? 'selected' : ''}>Framework</option>
                        <option value="database" ${skill?.category === 'database' ? 'selected' : ''}>Database</option>
                        <option value="tool" ${skill?.category === 'tool' ? 'selected' : ''}>Tool</option>
                        <option value="soft_skill" ${skill?.category === 'soft_skill' ? 'selected' : ''}>Soft Skill</option>
                        <option value="language" ${skill?.category === 'language' ? 'selected' : ''}>Language</option>
                        <option value="other" ${skill?.category === 'other' ? 'selected' : ''}>Other</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Proficiency</label>
                    <select name="proficiency" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                        <option value="beginner" ${skill?.proficiency === 'beginner' ? 'selected' : ''}>Beginner</option>
                        <option value="intermediate" ${skill?.proficiency === 'intermediate' ? 'selected' : ''}>Intermediate</option>
                        <option value="advanced" ${skill?.proficiency === 'advanced' ? 'selected' : ''}>Advanced</option>
                        <option value="expert" ${skill?.proficiency === 'expert' ? 'selected' : ''}>Expert</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Years Experience</label>
                    <input type="number" name="years_experience" min="0" step="0.5" value="${skill?.years_experience || ''}"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Keywords (comma-separated)</label>
                    <input type="text" name="keywords" value="${skill?.keywords?.join(', ') || ''}"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                        placeholder="py, python3, scripting">
                </div>
            </div>
        `;
        openModal(skill ? 'Edit Skill' : 'Add Skill', html, 'skill', skill);
    }

    // =====================
    // Projects
    // =====================
    
    function renderProjects(projects) {
        const container = document.getElementById('projectsList');
        const noProjects = document.getElementById('noProjects');
        
        if (!projects || projects.length === 0) {
            container.innerHTML = '';
            noProjects.classList.remove('hidden');
            return;
        }
        
        noProjects.classList.add('hidden');
        container.innerHTML = projects.map(project => `
            <div class="p-4 bg-gray-50 rounded-lg" data-project-id="${project.id}">
                <div class="flex items-start justify-between">
                    <div>
                        <h4 class="font-semibold">${escapeHtml(project.name)}</h4>
                        <p class="text-sm text-gray-600 mt-1">${escapeHtml(project.description || '')}</p>
                        <div class="flex flex-wrap gap-2 mt-2">
                            ${(project.technologies || []).map(tech => 
                                `<span class="px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-700">${escapeHtml(tech)}</span>`
                            ).join('')}
                        </div>
                        ${project.github_url ? `<a href="${project.github_url}" target="_blank" class="text-sm text-blue-500 hover:underline mt-2 inline-block"><i class="fab fa-github mr-1"></i>GitHub</a>` : ''}
                    </div>
                    <div class="flex gap-2">
                        <button type="button" class="text-gray-400 hover:text-blue-500 edit-project" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="text-gray-400 hover:text-red-500 delete-project" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add event listeners
        container.querySelectorAll('.edit-project').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const projectId = e.target.closest('[data-project-id]').dataset.projectId;
                const project = projects.find(p => p.id == projectId);
                openProjectModal(project);
            });
        });
        
        container.querySelectorAll('.delete-project').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const projectId = e.target.closest('[data-project-id]').dataset.projectId;
                if (confirm('Delete this project?')) {
                    await deleteItem('projects', projectId);
                }
            });
        });
    }

    function openProjectModal(project = null) {
        const html = `
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
                    <input type="text" name="name" required value="${project?.name || ''}"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea name="description" rows="3"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">${project?.description || ''}</textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Technologies (comma-separated)</label>
                    <input type="text" name="technologies" value="${project?.technologies?.join(', ') || ''}"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                        placeholder="Python, Flask, PostgreSQL">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Project URL</label>
                        <input type="url" name="url" value="${project?.url || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">GitHub URL</label>
                        <input type="url" name="github_url" value="${project?.github_url || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input type="date" name="start_date" value="${project?.start_date || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                        <input type="date" name="end_date" value="${project?.end_date || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Highlights (one per line)</label>
                    <textarea name="highlights" rows="3"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                        placeholder="Implemented feature X&#10;Improved performance by Y%">${project?.highlights?.join('\n') || ''}</textarea>
                </div>
            </div>
        `;
        openModal(project ? 'Edit Project' : 'Add Project', html, 'project', project);
    }

    // =====================
    // Education
    // =====================
    
    function renderEducation(education) {
        const container = document.getElementById('educationList');
        const noEducation = document.getElementById('noEducation');
        
        if (!education || education.length === 0) {
            container.innerHTML = '';
            noEducation.classList.remove('hidden');
            return;
        }
        
        noEducation.classList.add('hidden');
        container.innerHTML = education.map(edu => `
            <div class="p-4 bg-gray-50 rounded-lg" data-education-id="${edu.id}">
                <div class="flex items-start justify-between">
                    <div>
                        <h4 class="font-semibold">${escapeHtml(edu.institution)}</h4>
                        <p class="text-sm text-gray-700">${escapeHtml(edu.degree)}${edu.field ? ` in ${escapeHtml(edu.field)}` : ''}</p>
                        <p class="text-sm text-gray-500">
                            ${edu.start_date || 'N/A'} - ${edu.end_date || 'Present'}
                            ${edu.gpa ? ` • GPA: ${edu.gpa}` : ''}
                        </p>
                    </div>
                    <div class="flex gap-2">
                        <button type="button" class="text-gray-400 hover:text-blue-500 edit-education" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="text-gray-400 hover:text-red-500 delete-education" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add event listeners
        container.querySelectorAll('.edit-education').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const eduId = e.target.closest('[data-education-id]').dataset.educationId;
                const edu = education.find(e => e.id == eduId);
                openEducationModal(edu);
            });
        });
        
        container.querySelectorAll('.delete-education').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const eduId = e.target.closest('[data-education-id]').dataset.educationId;
                if (confirm('Delete this education entry?')) {
                    await deleteItem('education', eduId);
                }
            });
        });
    }

    function openEducationModal(edu = null) {
        const html = `
            <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Institution *</label>
                        <input type="text" name="institution" required value="${edu?.institution || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Degree *</label>
                        <input type="text" name="degree" required value="${edu?.degree || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                            placeholder="Bachelor of Science">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Field of Study</label>
                        <input type="text" name="field" value="${edu?.field || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                            placeholder="Computer Science">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input type="text" name="start_date" value="${edu?.start_date || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                            placeholder="2020">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                        <input type="text" name="end_date" value="${edu?.end_date || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                            placeholder="2024 or Expected 2024">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">GPA</label>
                        <input type="text" name="gpa" value="${edu?.gpa || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                            placeholder="3.8/4.0">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                        <input type="text" name="location" value="${edu?.location || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Achievements (one per line)</label>
                    <textarea name="achievements" rows="3"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                        placeholder="Dean's List&#10;Relevant coursework: ...">${edu?.achievements?.join('\n') || ''}</textarea>
                </div>
            </div>
        `;
        openModal(edu ? 'Edit Education' : 'Add Education', html, 'education', edu);
    }

    // =====================
    // Experience
    // =====================
    
    function renderExperience(experience) {
        const container = document.getElementById('experienceList');
        const noExperience = document.getElementById('noExperience');
        
        if (!experience || experience.length === 0) {
            container.innerHTML = '';
            noExperience.classList.remove('hidden');
            return;
        }
        
        noExperience.classList.add('hidden');
        container.innerHTML = experience.map(exp => `
            <div class="p-4 bg-gray-50 rounded-lg" data-experience-id="${exp.id}">
                <div class="flex items-start justify-between">
                    <div>
                        <h4 class="font-semibold">${escapeHtml(exp.title)}</h4>
                        <p class="text-sm text-gray-700">${escapeHtml(exp.company)}${exp.location ? ` • ${escapeHtml(exp.location)}` : ''}</p>
                        <p class="text-sm text-gray-500">
                            ${exp.start_date || 'N/A'} - ${exp.is_current ? 'Present' : (exp.end_date || 'N/A')}
                        </p>
                        <p class="text-sm text-gray-600 mt-2">${escapeHtml(exp.description || '')}</p>
                        <div class="flex flex-wrap gap-2 mt-2">
                            ${(exp.technologies || []).map(tech => 
                                `<span class="px-2 py-0.5 text-xs rounded bg-purple-100 text-purple-700">${escapeHtml(tech)}</span>`
                            ).join('')}
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <button type="button" class="text-gray-400 hover:text-blue-500 edit-experience" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="text-gray-400 hover:text-red-500 delete-experience" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Add event listeners
        container.querySelectorAll('.edit-experience').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const expId = e.target.closest('[data-experience-id]').dataset.experienceId;
                const exp = experience.find(e => e.id == expId);
                openExperienceModal(exp);
            });
        });
        
        container.querySelectorAll('.delete-experience').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const expId = e.target.closest('[data-experience-id]').dataset.experienceId;
                if (confirm('Delete this experience entry?')) {
                    await deleteItem('experience', expId);
                }
            });
        });
    }

    function openExperienceModal(exp = null) {
        const html = `
            <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Job Title *</label>
                        <input type="text" name="title" required value="${exp?.title || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Company *</label>
                        <input type="text" name="company" required value="${exp?.company || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                        <input type="text" name="location" value="${exp?.location || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                    </div>
                    <div class="flex items-center pt-6">
                        <label class="inline-flex items-center">
                            <input type="checkbox" name="is_current" ${exp?.is_current ? 'checked' : ''}
                                class="mr-2 accent-emerald-600">
                            <span class="text-sm text-gray-700">Currently working here</span>
                        </label>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                        <input type="text" name="start_date" value="${exp?.start_date || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                            placeholder="Jan 2023">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                        <input type="text" name="end_date" value="${exp?.end_date || ''}"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                            placeholder="Jun 2023">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea name="description" rows="3"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">${exp?.description || ''}</textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Technologies Used (comma-separated)</label>
                    <input type="text" name="technologies" value="${exp?.technologies?.join(', ') || ''}"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Achievements (one per line)</label>
                    <textarea name="achievements" rows="3"
                        class="w-full border border-gray-300 rounded-lg px-3 py-2 focus-accent"
                        placeholder="Developed feature X&#10;Led project Y">${exp?.achievements?.join('\n') || ''}</textarea>
                </div>
            </div>
        `;
        openModal(exp ? 'Edit Experience' : 'Add Experience', html, 'experience', exp);
    }

    // =====================
    // Modal Submit Handler
    // =====================
    
    async function handleModalSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        // Process array fields
        if (data.keywords) data.keywords = data.keywords.split(',').map(s => s.trim()).filter(Boolean);
        if (data.technologies) data.technologies = data.technologies.split(',').map(s => s.trim()).filter(Boolean);
        if (data.highlights) data.highlights = data.highlights.split('\n').map(s => s.trim()).filter(Boolean);
        if (data.achievements) data.achievements = data.achievements.split('\n').map(s => s.trim()).filter(Boolean);
        if (data.is_current !== undefined) data.is_current = formData.has('is_current');
        if (data.years_experience) data.years_experience = parseFloat(data.years_experience);
        
        const isEdit = editingItem !== null;
        const endpoint = `/api/cv/${currentModal}${currentModal === 'skill' ? 's' : currentModal === 'project' ? 's' : ''}`;
        
        try {
            let response;
            if (isEdit) {
                response = await fetch(`${endpoint}/${editingItem.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
            } else {
                response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
            }
            
            const result = await response.json();
            if (result.success || response.ok) {
                showToast(`${currentModal} ${isEdit ? 'updated' : 'added'} successfully!`, 'success');
                closeModal();
                loadProfile();
            } else {
                showToast(result.error || 'Operation failed', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Operation failed', 'error');
        }
    }

    async function deleteItem(type, id) {
        try {
            const response = await fetch(`/api/cv/${type}/${id}`, {
                method: 'DELETE',
            });
            
            const result = await response.json();
            if (result.success || response.ok) {
                showToast(`${type} deleted successfully!`, 'success');
                loadProfile();
            } else {
                showToast(result.error || 'Delete failed', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Delete failed', 'error');
        }
    }

    // =====================
    // Document Generation
    // =====================
    
    function getJobData() {
        const form = document.getElementById('generateForm');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Process skills array
        if (data.skills) {
            data.skills = data.skills.split(',').map(s => s.trim()).filter(Boolean);
        } else {
            data.skills = [];
        }
        
        return data;
    }

    async function handleAnalyzeMatch() {
        const data = getJobData();
        
        if (!data.title || !data.company) {
            showToast('Please fill in at least job title and company', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/cv/analyze-match', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            
            const result = await response.json();
            if (result.success && result.match_result) {
                displayMatchAnalysis(result.match_result);
            } else {
                showToast(result.error || 'Analysis failed', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Analysis failed', 'error');
        }
    }

    function displayMatchAnalysis(match) {
        const container = document.getElementById('matchAnalysis');
        const scoreCircle = document.getElementById('matchScoreCircle');
        const scoreValue = document.getElementById('matchScoreValue');
        const detailsContainer = document.getElementById('matchDetails');
        
        // Show container
        container.classList.remove('hidden');
        
        // Animate score circle
        const score = match.overall_score;
        scoreCircle.style.strokeDasharray = `${score}, 100`;
        scoreValue.textContent = `${Math.round(score)}%`;
        
        // Set color based on score
        if (score >= 70) {
            scoreCircle.style.stroke = '#10b981'; // green
        } else if (score >= 50) {
            scoreCircle.style.stroke = '#f59e0b'; // yellow
        } else {
            scoreCircle.style.stroke = '#ef4444'; // red
        }
        
        // Display matched skills
        const matchedSkillsSection = document.getElementById('matchedSkillsSection');
        const matchedSkillsList = document.getElementById('matchedSkillsList');
        
        if (match.matched_skills && match.matched_skills.length > 0) {
            matchedSkillsSection.classList.remove('hidden');
            matchedSkillsList.innerHTML = match.matched_skills.map(skill => 
                `<span class="px-2 py-1 text-sm rounded bg-green-100 text-green-700">${escapeHtml(skill)}</span>`
            ).join('');
        } else {
            matchedSkillsSection.classList.add('hidden');
        }
        
        // Display missing skills
        const missingSkillsSection = document.getElementById('missingSkillsSection');
        const missingSkillsList = document.getElementById('missingSkillsList');
        
        if (match.missing_skills && match.missing_skills.length > 0) {
            missingSkillsSection.classList.remove('hidden');
            missingSkillsList.innerHTML = match.missing_skills.map(skill => 
                `<span class="px-2 py-1 text-sm rounded bg-yellow-100 text-yellow-700">${escapeHtml(skill)}</span>`
            ).join('');
        } else {
            missingSkillsSection.classList.add('hidden');
        }
        
        // Display recommendations
        if (match.recommendations && match.recommendations.length > 0) {
            detailsContainer.innerHTML = `
                <h4 class="text-sm font-medium text-gray-700 mb-2">Recommendations:</h4>
                <ul class="text-sm text-gray-600 space-y-1">
                    ${match.recommendations.map(rec => `<li>• ${escapeHtml(rec)}</li>`).join('')}
                </ul>
            `;
        } else {
            detailsContainer.innerHTML = '';
        }
    }

    async function handleGenerate(e) {
        e.preventDefault();
        
        const data = getJobData();
        data.compile_pdf = document.getElementById('compile_pdf').checked;
        
        const genCv = document.getElementById('gen_cv').checked;
        const genCoverLetter = document.getElementById('gen_cover_letter').checked;
        
        if (!data.title || !data.company || !data.description) {
            showToast('Please fill in job title, company, and description', 'error');
            return;
        }
        
        if (!genCv && !genCoverLetter) {
            showToast('Please select at least one document type to generate', 'error');
            return;
        }
        
        try {
            let endpoint, result;
            
            if (genCv && genCoverLetter) {
                const response = await fetch('/api/cv/generate/both', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
                result = await response.json();
                displayGenerationResult([result.cv, result.cover_letter]);
            } else if (genCv) {
                const response = await fetch('/api/cv/generate/cv', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
                result = await response.json();
                displayGenerationResult([result]);
            } else {
                const response = await fetch('/api/cv/generate/cover-letter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
                result = await response.json();
                displayGenerationResult([result]);
            }
            
            showToast('Documents generated successfully!', 'success');
            
        } catch (error) {
            console.error('Error:', error);
            showToast('Generation failed', 'error');
        }
    }

    function displayGenerationResult(results) {
        const container = document.getElementById('generationResult');
        const docsContainer = document.getElementById('generatedDocuments');
        
        container.classList.remove('hidden');
        
        docsContainer.innerHTML = results.filter(r => r && r.success).map(result => {
            const doc = result.document;
            if (!doc) return '';
            
            return `
                <div class="p-4 bg-gray-50 rounded-lg flex items-center justify-between">
                    <div>
                        <div class="flex items-center gap-2">
                            <i class="fas fa-${doc.document_type === 'cv' ? 'file-alt' : 'envelope'} text-emerald-600"></i>
                            <span class="font-medium">${doc.document_type === 'cv' ? 'CV' : 'Cover Letter'}</span>
                        </div>
                        <p class="text-sm text-gray-500">${escapeHtml(doc.company_name)} - ${escapeHtml(doc.job_title)}</p>
                        ${doc.match_score ? `<p class="text-sm text-gray-400">Match: ${Math.round(doc.match_score)}%</p>` : ''}
                    </div>
                    ${doc.pdf_path ? `
                        <a href="/api/cv/documents/${doc.id}/download" class="btn-primary px-3 py-1 rounded text-sm">
                            <i class="fas fa-download mr-1"></i>Download PDF
                        </a>
                    ` : '<span class="text-sm text-gray-400">PDF not compiled</span>'}
                </div>
            `;
        }).join('');
    }

    // =====================
    // Documents List
    // =====================
    
    async function loadDocuments() {
        try {
            const response = await fetch('/api/cv/documents');
            const data = await response.json();
            
            const container = document.getElementById('documentsList');
            const noDocuments = document.getElementById('noDocuments');
            
            if (data.success && data.documents && data.documents.length > 0) {
                noDocuments.classList.add('hidden');
                container.innerHTML = data.documents.map(doc => `
                    <div class="p-4 bg-gray-50 rounded-lg flex items-center justify-between">
                        <div>
                            <div class="flex items-center gap-2">
                                <i class="fas fa-${doc.document_type === 'cv' ? 'file-alt' : 'envelope'} text-emerald-600"></i>
                                <span class="font-medium">${doc.document_type === 'cv' ? 'CV' : 'Cover Letter'}</span>
                                <span class="text-sm text-gray-400">${formatDate(doc.created_at)}</span>
                            </div>
                            <p class="text-sm text-gray-700">${escapeHtml(doc.company_name || 'Unknown')} - ${escapeHtml(doc.job_title || 'Unknown')}</p>
                            ${doc.match_score ? `<p class="text-sm text-gray-400">Match score: ${Math.round(doc.match_score)}%</p>` : ''}
                        </div>
                        ${doc.pdf_path ? `
                            <a href="/api/cv/documents/${doc.id}/download" class="btn-secondary px-3 py-1 rounded text-sm">
                                <i class="fas fa-download mr-1"></i>Download
                            </a>
                        ` : ''}
                    </div>
                `).join('');
            } else {
                container.innerHTML = '';
                noDocuments.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }

    // =====================
    // Utilities
    // =====================
    
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
    }

    function showToast(message, type = 'info') {
        // Use existing toast function from app.js if available
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            // Fallback to alert
            alert(message);
        }
    }
});
