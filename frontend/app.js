const { useState, useEffect, useMemo } = React;

const API_BASE = "/api";

// Icon component wrapper using Lucide
function Icon({ name, className = "w-5 h-5", ...props }) {
  useEffect(() => {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }, [name]);

  return <i data-lucide={name} className={className} {...props}></i>;
}

// Toast Notification Component
function Toast({ message, type = "info", onClose }) {
  if (!message) return null;
  const bgColors = {
    info: "bg-[#2A2A2A] text-white border-l-4 border-[#5E83AE]",
    success: "bg-[#2E7D32] text-white",
    error: "bg-[#DC2626] text-white"
  };

  return (
    <div className={`fixed bottom-6 right-6 z-50 px-5 py-3 rounded-lg shadow-xl flex items-center gap-3 transition-smooth ${bgColors[type] || bgColors.info}`}>
      <span className="text-sm">{message}</span>
      <button onClick={onClose} className="opacity-80 hover:opacity-100 text-lg font-bold ml-2">×</button>
    </div>
  );
}

// Confirmation Modal Component
function ConfirmModal({ isOpen, title, message, confirmText = "Confirm", confirmColor = "bg-red-600 hover:bg-red-700", onConfirm, onCancel }) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl p-6 max-w-md w-full border border-[#EAE5D9] shadow-xl space-y-4">
        <h3 className="font-bold text-lg text-[#2A2A2A]">{title}</h3>
        <p className="text-xs text-gray-600 leading-relaxed">{message}</p>
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold transition-smooth"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 rounded-xl text-white text-xs font-bold transition-smooth shadow-xs ${confirmColor}`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  // Authentication State
  const [userType, setUserType] = useState(() => localStorage.getItem("cp_user_type") || null);
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem("cp_user_profile");
    return saved ? JSON.parse(saved) : null;
  });

  // Current Active Page / View
  const [currentView, setCurrentView] = useState("dashboard"); // dashboard, resume, recommendations, jobs_apply, skill_gap, roadmap | company_dashboard, create_job, matched_candidates, candidate_profile
  
  // Job Seeker Specific State
  const [recommendations, setRecommendations] = useState(null);
  const [selectedRoleForGap, setSelectedRoleForGap] = useState("fullstack-dev");
  const [skillGapData, setSkillGapData] = useState(null);
  const [roadmapData, setRoadmapData] = useState(null);
  const [appliedJobIds, setAppliedJobIds] = useState(new Set());
  const [allCompanyJobs, setAllCompanyJobs] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [showNotificationsModal, setShowNotificationsModal] = useState(false);

  // Company Specific State
  const [companyJobs, setCompanyJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [matchedCandidatesData, setMatchedCandidatesData] = useState(null);
  const [selectedCandidateDossier, setSelectedCandidateDossier] = useState(null);
  const [editingJob, setEditingJob] = useState(null); // For edit job modal
  const [interviewCandidateModal, setInterviewCandidateModal] = useState(null); // { candidate, job }

  // Common UI State
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [taxonomy, setTaxonomy] = useState({});
  const [news, setNews] = useState([]);

  const showToast = (msg, type = "info") => {
    setToast({ message: msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Persist session
  useEffect(() => {
    if (userType) {
      localStorage.setItem("cp_user_type", userType);
    } else {
      localStorage.removeItem("cp_user_type");
    }
  }, [userType]);

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem("cp_user_profile", JSON.stringify(currentUser));
    } else {
      localStorage.removeItem("cp_user_profile");
    }
  }, [currentUser]);

  // Initial Data Fetch
  useEffect(() => {
    fetchTaxonomy();
    fetchNews();
  }, []);

  const fetchTaxonomy = async () => {
    try {
      const res = await fetch(`${API_BASE}/resumes/taxonomy`);
      const data = await res.json();
      setTaxonomy(data);
    } catch (e) {
      console.error("Error fetching taxonomy:", e);
    }
  };

  const fetchNews = async () => {
    try {
      const res = await fetch(`${API_BASE}/news`);
      if (res.ok) {
        const data = await res.json();
        setNews(data);
      }
    } catch (e) {
      console.error("Error fetching news:", e);
    }
  };

  // Load User / Company data when logged in
  useEffect(() => {
    if (userType === "job_seeker" && currentUser?.id) {
      loadJobSeekerData(currentUser.id);
      fetchCandidateApplications(currentUser.id);
      fetchUserNotifications(currentUser.id);
      fetchAllJobs();
    } else if (userType === "company" && currentUser?.id) {
      loadCompanyData(currentUser.id);
    }
  }, [userType, currentUser?.id]);

  const loadJobSeekerData = async (candidateId) => {
    try {
      const res = await fetch(`${API_BASE}/auth/profile/${candidateId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.profile) {
          setCurrentUser(data.profile);
          fetchCurrentRoleRecommendations(data.profile.id);
        }
      }
    } catch (e) {
      console.error("Error loading candidate profile:", e);
    }
  };

  const loadCompanyData = async (companyId) => {
    try {
      const res = await fetch(`${API_BASE}/auth/profile/${companyId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.profile) {
          setCurrentUser(data.profile);
          fetchCompanyJobs(data.profile.id);
        }
      }
    } catch (e) {
      console.error("Error loading company profile:", e);
    }
  };

  const fetchCompanyJobs = async (companyId) => {
    try {
      const res = await fetch(`${API_BASE}/jobs?company_id=${companyId}`);
      if (res.ok) {
        const jobs = await res.json();
        setCompanyJobs(jobs);
        if (jobs.length > 0 && !selectedJobId) {
          setSelectedJobId(jobs[0].id);
        }
      }
    } catch (e) {
      console.error("Error fetching company jobs:", e);
    }
  };

  const fetchAllJobs = async () => {
    try {
      const res = await fetch(`${API_BASE}/jobs`);
      if (res.ok) {
        const jobs = await res.json();
        setAllCompanyJobs(jobs);
      }
    } catch (e) {
      console.error("Error fetching all jobs:", e);
    }
  };

  const fetchCandidateApplications = async (candidateId) => {
    try {
      const res = await fetch(`${API_BASE}/jobs/applications/candidate/${candidateId}`);
      if (res.ok) {
        const apps = await res.json();
        const appliedSet = new Set(apps.map(a => a.job_id));
        setAppliedJobIds(appliedSet);
      }
    } catch (e) {
      console.error("Error fetching candidate applications:", e);
    }
  };

  const fetchUserNotifications = async (userId) => {
    try {
      const res = await fetch(`${API_BASE}/notifications/${userId}`);
      if (res.ok) {
        const notifs = await res.json();
        setNotifications(notifs);
      }
    } catch (e) {
      console.error("Error fetching notifications:", e);
    }
  };

  const fetchCurrentRoleRecommendations = async (candidateId) => {
    try {
      const res = await fetch(`${API_BASE}/matching/current-roles/${candidateId}`);
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data);
      }
    } catch (e) {
      console.error("Error fetching recommendations:", e);
    }
  };

  const fetchSkillGap = async (roleId) => {
    if (!currentUser) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/matching/skill-gap/${currentUser.id}/${roleId}`);
      const data = await res.json();
      setSkillGapData(data);
      setSelectedRoleForGap(roleId);
      setCurrentView("skill_gap");
    } catch (e) {
      showToast("Error analyzing skill gap", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchRoadmap = async (roleId) => {
    if (!currentUser) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/matching/roadmap/${currentUser.id}/${roleId}`);
      const data = await res.json();
      setRoadmapData(data);
      setSelectedRoleForGap(roleId);
      setCurrentView("roadmap");
    } catch (e) {
      showToast("Error generating learning roadmap", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchMatchedCandidatesForJob = async (jobId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/candidates`);
      const data = await res.json();
      setMatchedCandidatesData(data);
      setSelectedJobId(jobId);
      setCurrentView("matched_candidates");
    } catch (e) {
      showToast("Error finding matched candidates", "error");
    } finally {
      setLoading(false);
    }
  };

  const viewCandidateDossier = async (candidateId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/candidates/${candidateId}`);
      const data = await res.json();
      setSelectedCandidateDossier(data);
      setCurrentView("candidate_profile");
    } catch (e) {
      showToast("Error loading candidate profile", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyToJob = async (jobId) => {
    if (!currentUser) return;
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: currentUser.id, candidate_name: currentUser.name })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setAppliedJobIds(prev => new Set([...prev, jobId]));
        showToast("Application submitted successfully!", "success");
      } else {
        showToast(data.message || "Failed to apply.", "error");
      }
    } catch (e) {
      showToast("Error submitting application.", "error");
    }
  };

  const handleDeleteResume = async () => {
    if (!currentUser) return;
    try {
      const res = await fetch(`${API_BASE}/resumes/${currentUser.id}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setCurrentUser(data.candidate);
        setRecommendations(null);
        showToast("Resume deleted successfully.", "success");
      } else {
        showToast("Failed to delete resume.", "error");
      }
    } catch (e) {
      showToast("Error deleting resume.", "error");
    }
  };

  const handleDeleteJob = async (jobId) => {
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setCompanyJobs(prev => prev.filter(j => j.id !== jobId));
        showToast("Job requisition deleted successfully.", "success");
      } else {
        showToast("Failed to delete job.", "error");
      }
    } catch (e) {
      showToast("Error deleting job.", "error");
    }
  };

  const handleUpdateJob = async (jobId, updatedFields) => {
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedFields)
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setCompanyJobs(prev => prev.map(j => j.id === jobId ? data.job : j));
        setEditingJob(null);
        showToast("Job requisition updated successfully!", "success");
      } else {
        showToast("Failed to update job.", "error");
      }
    } catch (e) {
      showToast("Error updating job.", "error");
    }
  };

  const handleSetCandidateStatus = async (jobId, candidateId, statusData) => {
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/candidates/${candidateId}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(statusData)
      });
      const data = await res.json();
      if (res.ok && data.success) {
        showToast(statusData.status === "interview" ? "Interview scheduled and notification sent!" : "Rejection notification sent.", "success");
        setInterviewCandidateModal(null);
        // Refresh matched candidates view
        fetchMatchedCandidatesForJob(jobId);
      } else {
        showToast("Failed to update candidate status.", "error");
      }
    } catch (e) {
      showToast("Error updating status.", "error");
    }
  };

  const handleLogout = () => {
    setUserType(null);
    setCurrentUser(null);
    setRecommendations(null);
    setCompanyJobs([]);
    setMatchedCandidatesData(null);
    setAppliedJobIds(new Set());
    setCurrentView("dashboard");
    showToast("Logged out successfully.", "info");
  };

  // Re-trigger icon rendering
  useEffect(() => {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }, [currentView, userType, currentUser, recommendations, skillGapData, roadmapData, matchedCandidatesData, news, companyJobs, allCompanyJobs]);

  // If not logged in, render the dual Login/Sign Up portal
  if (!userType || !currentUser) {
    return (
      <div className="min-h-screen flex flex-col bg-[#F9F5ED] text-[#2A2A2A]">
        {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
        
        {/* Simple Clean Header */}
        <header className="bg-white border-b border-[#EAE5D9] sticky top-0 z-40 shadow-xs">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#2A2A2A] flex items-center justify-center text-[#F9F5ED] font-bold text-xl shadow-inner">
                CP
              </div>
              <div>
                <div className="font-bold text-lg leading-tight tracking-tight text-[#2A2A2A]">
                  CareerPulse <span className="text-xs px-2 py-0.5 rounded-full bg-[#5E83AE] text-white font-medium">ADVISOR</span>
                </div>
                <p className="text-xs text-gray-500 hidden sm:block">Personalized Career Progression & Skill Matching</p>
              </div>
            </div>
          </div>
        </header>

        {/* Separated Login / Sign Up Portal */}
        <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-12 flex flex-col justify-center">
          <AuthPortalView
            onLoginSuccess={(role, profile) => {
              setUserType(role);
              setCurrentUser(profile);
              setCurrentView(role === "job_seeker" ? "dashboard" : "company_dashboard");
              showToast(`Welcome back, ${profile.name}!`, "success");
            }}
            showToast={showToast}
          />
        </main>

        <footer className="bg-white border-t border-[#EAE5D9] py-6 text-center text-xs text-gray-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <p>© 2026 CareerPulse Advisor. Personalized Career & Employment Platform.</p>
            <div className="flex items-center gap-4 text-gray-600">
              <span className="font-semibold text-[#5E83AE]">Skill-Based Career Matching</span>
            </div>
          </div>
        </footer>
      </div>
    );
  }

  // Logged-in application layout
  return (
    <div className="min-h-screen flex flex-col bg-[#F9F5ED] text-[#2A2A2A]">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* Navigation Bar */}
      <header className="bg-white border-b border-[#EAE5D9] sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentView(userType === "job_seeker" ? "dashboard" : "company_dashboard")}>
            <div className="w-10 h-10 rounded-xl bg-[#2A2A2A] flex items-center justify-center text-[#F9F5ED] font-bold text-xl shadow-inner">
              CP
            </div>
            <div>
              <div className="font-bold text-lg leading-tight tracking-tight text-[#2A2A2A] flex items-center gap-2">
                CareerPulse <span className="text-xs px-2 py-0.5 rounded-full bg-[#5E83AE] text-white font-medium">ADVISOR</span>
              </div>
              <p className="text-xs text-gray-500 hidden sm:block">
                {userType === "job_seeker" ? "Job Seeker Workspace" : "Company Talent Console"}
              </p>
            </div>
          </div>

          {/* Navigation Links based STRICTLY on User Role */}
          <nav className="hidden md:flex items-center gap-1.5">
            {userType === "job_seeker" ? (
              <>
                <button
                  onClick={() => setCurrentView("dashboard")}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentView === "dashboard" ? "bg-[#2A2A2A] text-white" : "text-gray-700 hover:bg-[#F3EFE6]"}`}
                >
                  Home
                </button>
                <button
                  onClick={() => setCurrentView("resume")}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentView === "resume" ? "bg-[#2A2A2A] text-white" : "text-gray-700 hover:bg-[#F3EFE6]"}`}
                >
                  Resume & Skills
                </button>
                <button
                  onClick={() => setCurrentView("jobs_apply")}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentView === "jobs_apply" ? "bg-[#2A2A2A] text-white" : "text-gray-700 hover:bg-[#F3EFE6]"}`}
                >
                  Jobs & Apply
                </button>
                <button
                  onClick={() => setCurrentView("recommendations")}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentView === "recommendations" ? "bg-[#2A2A2A] text-white" : "text-gray-700 hover:bg-[#F3EFE6]"}`}
                >
                  Recommended Roles
                </button>
                <button
                  onClick={() => {
                    if (selectedRoleForGap) {
                      fetchSkillGap(selectedRoleForGap);
                    } else {
                      setCurrentView("recommendations");
                    }
                  }}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentView === "skill_gap" || currentView === "roadmap" ? "bg-[#2A2A2A] text-white" : "text-gray-700 hover:bg-[#F3EFE6]"}`}
                >
                  Growth & Roadmap
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setCurrentView("company_dashboard")}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentView === "company_dashboard" ? "bg-[#2A2A2A] text-white" : "text-gray-700 hover:bg-[#F3EFE6]"}`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setCurrentView("create_job")}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentView === "create_job" ? "bg-[#2A2A2A] text-white" : "text-gray-700 hover:bg-[#F3EFE6]"}`}
                >
                  + Post Job Requisition
                </button>
              </>
            )}
          </nav>

          {/* Right Side: Logged-in User Profile & Logout */}
          <div className="flex items-center gap-3">
            {/* Job Seeker Notifications Bell */}
            {userType === "job_seeker" && (
              <button
                onClick={() => setShowNotificationsModal(true)}
                className="relative p-2 rounded-lg bg-[#F0ECE1] hover:bg-[#E2DDD0] text-gray-700 transition-smooth"
                title="View Notifications"
              >
                <span className="text-base">🔔</span>
                {notifications.length > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-600 text-white rounded-full text-[10px] font-bold flex items-center justify-center">
                    {notifications.length}
                  </span>
                )}
              </button>
            )}

            <div className="text-right hidden sm:block">
              <div className="text-xs font-bold text-[#2A2A2A]">{currentUser.name}</div>
              <div className="text-[11px] text-gray-500">
                {userType === "job_seeker" ? (currentUser.title || "Job Seeker") : (currentUser.industry || "Company")}
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="px-3 py-1.5 rounded-lg bg-[#F0ECE1] hover:bg-[#E2DDD0] text-[#2A2A2A] text-xs font-semibold transition-smooth border border-[#D5CEBF]"
              title="Log out of account"
            >
              Log Out
            </button>
          </div>

        </div>
      </header>

      {/* Main Body Content Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-[#5E83AE] border-t-transparent rounded-full animate-spin"></div>
            <span className="ml-3 text-sm font-medium text-gray-600">Matching skills & analyzing data...</span>
          </div>
        )}

        {!loading && (
          <>
            {/* JOB SEEKER VIEWS */}
            {userType === "job_seeker" && (
              <>
                {currentView === "dashboard" && (
                  <JobSeekerCleanDashboardView
                    candidate={currentUser}
                    news={news}
                    onNavigate={(view) => setCurrentView(view)}
                    onExploreCategory={(roleId) => {
                      fetchSkillGap(roleId);
                    }}
                  />
                )}

                {currentView === "resume" && (
                  <ResumeSkillAnalysisView
                    candidate={currentUser}
                    taxonomy={taxonomy}
                    onDeleteResume={handleDeleteResume}
                    onUpdateCandidate={(updated) => {
                      setCurrentUser(updated);
                      fetchCurrentRoleRecommendations(updated.id);
                      showToast("Skills updated successfully!", "success");
                    }}
                    showToast={showToast}
                  />
                )}

                {currentView === "jobs_apply" && (
                  <JobSeekerJobsApplyView
                    candidate={currentUser}
                    jobs={allCompanyJobs}
                    appliedJobIds={appliedJobIds}
                    onApply={handleApplyToJob}
                    onNavigateToResume={() => setCurrentView("resume")}
                  />
                )}

                {currentView === "recommendations" && (
                  <RecommendedRolesView
                    candidate={currentUser}
                    recommendations={recommendations}
                    onAnalyzeGap={(roleId) => {
                      fetchSkillGap(roleId);
                    }}
                    onGenerateRoadmap={(roleId) => {
                      fetchRoadmap(roleId);
                    }}
                    onNavigateToResume={() => setCurrentView("resume")}
                  />
                )}

                {currentView === "skill_gap" && (
                  <RoleDetailsSkillGapView
                    gapData={skillGapData}
                    candidate={currentUser}
                    onGenerateRoadmap={(roleId) => fetchRoadmap(roleId)}
                    onBack={() => setCurrentView("recommendations")}
                    onSelectAnotherRole={(roleId) => fetchSkillGap(roleId)}
                  />
                )}

                {currentView === "roadmap" && (
                  <LearningRoadmapView
                    roadmap={roadmapData}
                    candidate={currentUser}
                    onBack={() => setCurrentView("skill_gap")}
                    showToast={showToast}
                  />
                )}
              </>
            )}

            {/* COMPANY VIEWS */}
            {userType === "company" && (
              <>
                {currentView === "company_dashboard" && (
                  <CompanyDashboardView
                    company={currentUser}
                    jobs={companyJobs}
                    onCreateJob={() => setCurrentView("create_job")}
                    onEditJob={(job) => setEditingJob(job)}
                    onDeleteJob={handleDeleteJob}
                    onViewMatches={(jobId) => fetchMatchedCandidatesForJob(jobId)}
                  />
                )}

                {currentView === "create_job" && (
                  <CreateJobView
                    company={currentUser}
                    onJobCreated={(newJob) => {
                      fetchCompanyJobs(currentUser.id);
                      showToast(`Job requisition '${newJob.title}' created successfully!`, "success");
                      fetchMatchedCandidatesForJob(newJob.id);
                    }}
                    onCancel={() => setCurrentView("company_dashboard")}
                    showToast={showToast}
                  />
                )}

                {currentView === "matched_candidates" && (
                  <MatchedCandidatesView
                    matchData={matchedCandidatesData}
                    onSelectInterview={(cand, job) => setInterviewCandidateModal({ candidate: cand, job })}
                    onRejectCandidate={(candId, jobId) => {
                      handleSetCandidateStatus(jobId, candId, { status: "rejected" });
                    }}
                    onViewCandidate={(candId) => viewCandidateDossier(candId)}
                    onBack={() => setCurrentView("company_dashboard")}
                  />
                )}

                {currentView === "candidate_profile" && (
                  <CandidateProfileView
                    candidate={selectedCandidateDossier}
                    currentJob={matchedCandidatesData?.job}
                    onSelectInterview={(cand, job) => setInterviewCandidateModal({ candidate: cand, job })}
                    onRejectCandidate={(candId, jobId) => {
                      handleSetCandidateStatus(jobId, candId, { status: "rejected" });
                    }}
                    onBack={() => setCurrentView("matched_candidates")}
                  />
                )}
              </>
            )}
          </>
        )}

      </main>

      {/* Edit Job Modal */}
      {editingJob && (
        <EditJobModal
          job={editingJob}
          onClose={() => setEditingJob(null)}
          onSave={(jobId, fields) => handleUpdateJob(jobId, fields)}
        />
      )}

      {/* Interview Selection Modal */}
      {interviewCandidateModal && (
        <InterviewSelectionModal
          candidate={interviewCandidateModal.candidate}
          job={interviewCandidateModal.job}
          onClose={() => setInterviewCandidateModal(null)}
          onSubmit={(statusData) => handleSetCandidateStatus(interviewCandidateModal.job.id, interviewCandidateModal.candidate.candidate_id || interviewCandidateModal.candidate.id, statusData)}
        />
      )}

      {/* Job Seeker Notifications Modal */}
      {showNotificationsModal && (
        <NotificationsModal
          notifications={notifications}
          onClose={() => setShowNotificationsModal(false)}
        />
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-[#EAE5D9] py-6 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>© 2026 CareerPulse Advisor. Personalized Career & Employment Platform.</p>
          <div className="flex items-center gap-4 text-gray-600">
            <span>Skill-Based Career Matching</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            <span className="font-semibold text-[#5E83AE]">Strict Qualification Matching Active</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

// ----------------------------------------------------
// AUTH PORTAL: Separate Login & Sign Up
// ----------------------------------------------------
function AuthPortalView({ onLoginSuccess, showToast }) {
  const [activeTab, setActiveTab] = useState("job_seeker");
  const [authMode, setAuthMode] = useState("login");

  // Form Fields
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [title, setTitle] = useState("");
  const [industry, setIndustry] = useState("Technology");
  const [location, setLocation] = useState("Remote");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      showToast("Please enter an email address.", "error");
      return;
    }

    setIsSubmitting(true);
    try {
      if (authMode === "login") {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim(), role_type: activeTab })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          onLoginSuccess(data.type, data.profile);
        } else {
          showToast(data.detail || "Login failed. Check your email or sign up.", "error");
        }
      } else {
        const endpoint = activeTab === "job_seeker" ? `${API_BASE}/auth/register/job-seeker` : `${API_BASE}/auth/register/company`;
        const payload = activeTab === "job_seeker"
          ? { name: name.trim(), email: email.trim(), phone: phone.trim(), title: title.trim() }
          : { name: name.trim(), email: email.trim(), industry, location, description };

        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.success) {
          onLoginSuccess(data.type, data.profile);
        } else {
          showToast(data.detail || "Registration failed.", "error");
        }
      }
    } catch (err) {
      showToast("Network error. Please try again.", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto w-full">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold font-heading text-[#2A2A2A] mb-2">
          Personalized Career & Employment Advisor
        </h1>
        <p className="text-sm text-gray-600 max-w-md mx-auto">
          Connect your existing skills to qualifying job roles, or find skilled talent matching your exact requirements.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-[#EAE5D9] shadow-sm overflow-hidden">
        
        {/* Role Selection Tabs */}
        <div className="grid grid-cols-2 border-b border-[#EAE5D9] bg-[#F9F5ED]">
          <button
            type="button"
            onClick={() => {
              setActiveTab("job_seeker");
              setAuthMode("login");
            }}
            className={`py-3.5 text-xs sm:text-sm font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === "job_seeker"
                ? "bg-white text-[#2A2A2A] border-b-2 border-[#5E83AE] shadow-xs"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            <span>👨‍💻</span> Job Seeker Access
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab("company");
              setAuthMode("login");
            }}
            className={`py-3.5 text-xs sm:text-sm font-bold transition-all flex items-center justify-center gap-2 ${
              activeTab === "company"
                ? "bg-white text-[#2A2A2A] border-b-2 border-[#5E83AE] shadow-xs"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            <span>🏢</span> Company Recruiter
          </button>
        </div>

        <div className="p-6 sm:p-8">
          
          {/* Toggle Login / Sign Up */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
            <div>
              <h2 className="text-lg font-bold text-[#2A2A2A]">
                {activeTab === "job_seeker" ? "Job Seeker" : "Company"} {authMode === "login" ? "Sign In" : "Registration"}
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                {authMode === "login" ? "Access your saved profile and matches" : "Create a new account to get started"}
              </p>
            </div>

            <div className="bg-[#F0ECE1] p-1 rounded-lg flex text-xs">
              <button
                type="button"
                onClick={() => setAuthMode("login")}
                className={`px-3 py-1 rounded-md font-semibold transition-all ${authMode === "login" ? "bg-white text-[#2A2A2A] shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setAuthMode("signup")}
                className={`px-3 py-1 rounded-md font-semibold transition-all ${authMode === "signup" ? "bg-white text-[#2A2A2A] shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
              >
                Sign Up
              </button>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            
            {authMode === "signup" && (
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                  {activeTab === "job_seeker" ? "Full Name *" : "Company Name *"}
                </label>
                <input
                  type="text"
                  required
                  placeholder={activeTab === "job_seeker" ? "e.g. Jane Doe" : "e.g. Acme Corporation"}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                Email Address *
              </label>
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
              />
            </div>

            {authMode === "signup" && activeTab === "job_seeker" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                    Phone Number (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="(555) 000-0000"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                    Current Title / Objective
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Software Engineer"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
                  />
                </div>
              </div>
            )}

            {authMode === "signup" && activeTab === "company" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                    Industry
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Financial Technology"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. New York, NY (Hybrid)"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs sm:text-sm font-bold transition-smooth shadow-sm mt-4"
            >
              {isSubmitting
                ? "Processing..."
                : authMode === "login"
                ? `Sign In as ${activeTab === "job_seeker" ? "Job Seeker" : "Company"}`
                : `Create ${activeTab === "job_seeker" ? "Job Seeker" : "Company"} Account`}
            </button>
          </form>

        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// VIEW 1: Clean Main Dashboard (Job Seeker Home) with Compact News
// ----------------------------------------------------
function JobSeekerCleanDashboardView({ candidate, news, onNavigate, onExploreCategory }) {
  if (!candidate) return null;

  const hasResume = !!candidate.resume_filename;
  const skillsCount = candidate.skills?.length || 0;

  return (
    <div className="space-y-10">
      
      {/* Motivational & Welcoming Intro Banner */}
      <div className="bg-[#2A2A2A] rounded-2xl p-6 sm:p-8 text-white relative overflow-hidden shadow-md">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#5E83AE]/30 text-[#A6C4E5] text-xs font-semibold mb-3 border border-[#5E83AE]/40">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Career Discovery Active
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-heading mb-2">
            Welcome, {candidate.name}
          </h1>
          <p className="text-gray-300 text-sm leading-relaxed">
            {hasResume
              ? `You currently have ${skillsCount} verified skills on file. Explore roles you already qualify for, browse job openings, or plan your next career step.`
              : "Get started by uploading your resume to discover job roles that match your existing skills without requiring extra training."}
          </p>
        </div>
      </div>

      {/* "What would you like to do?" Section */}
      <div className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-[#2A2A2A]">What would you like to do?</h2>
          <p className="text-xs text-gray-500">Choose an action below to manage your profile, apply for jobs, or discover career opportunities.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          
          {/* Card 1: Analyze Resume */}
          <div
            onClick={() => onNavigate("resume")}
            className="bg-white p-6 rounded-2xl border border-[#EAE5D9] card-hover cursor-pointer flex flex-col justify-between space-y-4 shadow-2xs"
          >
            <div className="space-y-2">
              <div className="w-10 h-10 rounded-xl bg-[#F0ECE1] text-[#5E83AE] flex items-center justify-center text-xl font-bold">
                📄
              </div>
              <h3 className="font-bold text-base text-[#2A2A2A]">Analyze Resume</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Upload your PDF resume to identify your skills, review extracted work experience, and manage your profile.
              </p>
            </div>
            <div className="text-xs font-bold text-[#5E83AE] flex items-center gap-1 pt-2">
              <span>{hasResume ? "Review Skills & Resume" : "Upload Resume"}</span>
              <span>→</span>
            </div>
          </div>

          {/* Card 2: Explore Roles & Apply */}
          <div
            onClick={() => onNavigate("jobs_apply")}
            className="bg-white p-6 rounded-2xl border border-[#EAE5D9] card-hover cursor-pointer flex flex-col justify-between space-y-4 shadow-2xs"
          >
            <div className="space-y-2">
              <div className="w-10 h-10 rounded-xl bg-[#E8F5E9] text-[#2E7D32] flex items-center justify-center text-xl font-bold">
                🎯
              </div>
              <h3 className="font-bold text-base text-[#2A2A2A]">Jobs & Apply</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                View posted job requisitions from companies, see your match percentage, and submit applications.
              </p>
            </div>
            <div className="text-xs font-bold text-[#2E7D32] flex items-center gap-1 pt-2">
              <span>Browse & Apply</span>
              <span>→</span>
            </div>
          </div>

          {/* Card 3: Plan Career Growth */}
          <div
            onClick={() => onExploreCategory("fullstack-dev")}
            className="bg-white p-6 rounded-2xl border border-[#EAE5D9] card-hover cursor-pointer flex flex-col justify-between space-y-4 shadow-2xs"
          >
            <div className="space-y-2">
              <div className="w-10 h-10 rounded-xl bg-[#FEF3C7] text-[#B45309] flex items-center justify-center text-xl font-bold">
                📈
              </div>
              <h3 className="font-bold text-base text-[#2A2A2A]">Plan Career Growth</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Select a target role, examine required skills, and follow a structured week-by-week learning roadmap.
              </p>
            </div>
            <div className="text-xs font-bold text-[#B45309] flex items-center gap-1 pt-2">
              <span>Explore Roadmaps</span>
              <span>→</span>
            </div>
          </div>

        </div>
      </div>

      {/* COMPACT INDUSTRY NEWS SECTION (Replaces "Explore Path") */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-[#2A2A2A] flex items-center gap-2">
              <span>📰</span> Industry News & Market Updates
            </h2>
            <p className="text-xs text-gray-500">
              Latest hiring trends and employment updates.
            </p>
          </div>
          <span className="text-xs font-semibold text-[#5E83AE] bg-blue-50 px-2.5 py-1 rounded-full border border-blue-100">
            Live Feed
          </span>
        </div>

        <div className="bg-white rounded-2xl border border-[#EAE5D9] shadow-2xs divide-y divide-gray-100 overflow-hidden">
          {news && news.length > 0 ? (
            news.map((item) => (
              <div key={item.id} className="p-4 hover:bg-[#F9F5ED] transition-smooth flex items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-[#F0ECE1] text-[#2A2A2A]">
                      {item.category}
                    </span>
                    <h3 className="text-xs sm:text-sm font-semibold text-[#2A2A2A] hover:text-[#5E83AE]">
                      {item.headline}
                    </h3>
                  </div>
                </div>
                <div className="text-[11px] text-gray-500 shrink-0 text-right font-medium">
                  {item.date_time}
                </div>
              </div>
            ))
          ) : (
            <div className="p-6 text-center text-xs text-gray-500">
              No news updates available at this moment.
            </div>
          )}
        </div>
      </div>

    </div>
  );
}

// ----------------------------------------------------
// VIEW 2: Resume & Skill Analysis with Delete Option
// ----------------------------------------------------
function ResumeSkillAnalysisView({ candidate, taxonomy, onDeleteResume, onUpdateCandidate, showToast }) {
  if (!candidate) return null;

  const [isUploading, setIsUploading] = useState(false);
  const [newSkillInput, setNewSkillInput] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showToast("Please upload a PDF file.", "error");
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("candidate_id", candidate.id);

    try {
      const res = await fetch(`${API_BASE}/resumes/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.success && data.candidate) {
        onUpdateCandidate(data.candidate);
        showToast(`Resume analyzed! ${data.parsed_data.skills?.length || 0} skills identified.`, "success");
      } else {
        showToast(data.detail || "Error analyzing resume", "error");
      }
    } catch (err) {
      showToast("Failed to upload and analyze resume.", "error");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveSkill = async (skillToRemove) => {
    const updated = (candidate.skills || []).filter(s => s !== skillToRemove);
    try {
      const res = await fetch(`${API_BASE}/resumes/update-skills`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: candidate.id, skills: updated })
      });
      const data = await res.json();
      if (data.success && data.candidate) {
        onUpdateCandidate(data.candidate);
      }
    } catch (err) {
      showToast("Error updating skills.", "error");
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkillInput.trim()) return;
    const skillName = newSkillInput.trim();
    if ((candidate.skills || []).includes(skillName)) {
      showToast("Skill already exists in profile.", "info");
      return;
    }

    const updated = [...(candidate.skills || []), skillName];
    try {
      const res = await fetch(`${API_BASE}/resumes/update-skills`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: candidate.id, skills: updated })
      });
      const data = await res.json();
      if (data.success && data.candidate) {
        onUpdateCandidate(data.candidate);
        setNewSkillInput("");
      }
    } catch (err) {
      showToast("Error adding skill.", "error");
    }
  };

  const hasSkills = candidate.skills && candidate.skills.length > 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold font-heading text-[#2A2A2A]">Resume & Skill Analysis</h1>
        <p className="text-sm text-gray-600 mt-1">
          Upload your PDF resume to extract and verify your skills, work experience, and educational background.
        </p>
      </div>

      {/* Upload Box with Delete Button */}
      <div className="bg-white p-8 rounded-2xl border-2 border-dashed border-[#D5CEBF] flex flex-col items-center justify-center text-center hover:border-[#5E83AE] transition-smooth">
        <div className="w-14 h-14 rounded-full bg-[#F0ECE1] flex items-center justify-center text-[#5E83AE] mb-3 text-2xl">
          📄
        </div>
        <h3 className="font-bold text-[#2A2A2A] text-base mb-1">
          {candidate.resume_filename ? "Upload Updated Resume (PDF)" : "Upload Your Resume (PDF)"}
        </h3>
        <p className="text-xs text-gray-500 mb-5 max-w-sm">
          Select a standard PDF file. Your resume will be processed to identify relevant technical and professional skills.
        </p>
        
        <label className="cursor-pointer px-6 py-3 rounded-xl bg-[#2A2A2A] hover:bg-[#3D4A59] text-white text-xs font-semibold transition-smooth shadow-sm">
          {isUploading ? "Analyzing Resume..." : "Browse & Upload PDF"}
          <input type="file" accept=".pdf" className="hidden" onChange={handleFileUpload} disabled={isUploading} />
        </label>

        {candidate.resume_filename && (
          <div className="mt-5 pt-4 border-t border-gray-100 flex flex-wrap items-center justify-center gap-3 text-xs">
            <span className="text-gray-600">Active Resume: <strong>{candidate.resume_filename}</strong></span>
            <span>•</span>
            <a
              href={`${API_BASE}/resumes/file/${candidate.resume_filename}`}
              target="_blank"
              className="font-bold text-[#5E83AE] hover:underline"
            >
              View PDF ↗
            </a>
            <span>•</span>
            {/* Small Delete Icon/Button with Confirmation */}
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="text-red-600 hover:text-red-800 font-semibold inline-flex items-center gap-1 hover:underline"
              title="Delete uploaded resume"
            >
              <span>🗑️</span> Delete Resume
            </button>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={showDeleteConfirm}
        title="Delete Uploaded Resume"
        message="Are you sure you want to delete your uploaded resume? This will clear your identified skills and profile data."
        confirmText="Delete Resume"
        confirmColor="bg-red-600 hover:bg-red-700"
        onConfirm={() => {
          setShowDeleteConfirm(false);
          onDeleteResume();
        }}
        onCancel={() => setShowDeleteConfirm(false)}
      />

      {/* Skills Matrix */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-[#2A2A2A]">
              Skills Found ({candidate.skills?.length || 0})
            </h2>
            <p className="text-xs text-gray-500">Skills identified from your profile. You can also add or remove skills manually.</p>
          </div>

          {/* Add Custom Skill Form */}
          <form onSubmit={handleAddSkill} className="flex gap-2">
            <input
              type="text"
              placeholder="Add skill (e.g. React, Python)..."
              value={newSkillInput}
              onChange={(e) => setNewSkillInput(e.target.value)}
              className="bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE] w-48 sm:w-60"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-semibold transition-smooth"
            >
              + Add
            </button>
          </form>
        </div>

        {/* Skill Badges or Empty State */}
        {!hasSkills ? (
          <div className="bg-[#F9F5ED] p-8 rounded-xl text-center border border-[#EAE5D9]">
            <p className="text-xs text-gray-500">
              No skills identified yet. Upload your PDF resume above or type a skill to add it manually.
            </p>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2 pt-2">
            {candidate.skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#F0ECE1] text-[#2A2A2A] text-xs font-medium border border-[#E2DDD0]"
              >
                <span>{skill}</span>
                <button
                  onClick={() => handleRemoveSkill(skill)}
                  className="text-gray-400 hover:text-red-600 font-bold text-sm ml-1"
                  title="Remove skill"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Extracted Work Experience & Education */}
      {(candidate.experience?.length > 0 || candidate.education?.length > 0 || candidate.summary) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Work Experience */}
          <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-4">
            <h3 className="font-bold text-[#2A2A2A] text-base flex items-center gap-2">
              <span>💼</span> Work Experience
            </h3>
            {candidate.experience && candidate.experience.length > 0 ? (
              <div className="space-y-4">
                {candidate.experience.map((exp, idx) => (
                  <div key={idx} className="border-l-2 border-[#5E83AE] pl-3 py-1 space-y-1">
                    <div className="font-bold text-xs text-[#2A2A2A]">{exp.title}</div>
                    <div className="text-[11px] text-[#5E83AE] font-medium">{exp.details}</div>
                    {exp.bullets && (
                      <ul className="text-xs text-gray-600 space-y-1 pt-1">
                        {exp.bullets.map((b, bIdx) => (
                          <li key={bIdx} className="list-disc ml-4">{b}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500">No work experience entries recorded yet.</p>
            )}
          </div>

          {/* Education & Summary */}
          <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-4">
            <h3 className="font-bold text-[#2A2A2A] text-base flex items-center gap-2">
              <span>🎓</span> Education & Summary
            </h3>
            
            <div className="space-y-3">
              <div>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Education</div>
                {candidate.education && candidate.education.length > 0 ? (
                  <div className="space-y-1">
                    {candidate.education.map((edu, idx) => (
                      <div key={idx} className="text-xs font-medium text-gray-800 bg-[#F9F5ED] p-2.5 rounded-lg border border-[#EAE5D9]">
                        {edu.institution_or_degree}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500">No education entries recorded yet.</p>
                )}
              </div>

              {candidate.summary && (
                <div className="pt-2">
                  <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Professional Summary</div>
                  <p className="text-xs text-gray-700 bg-[#F9F5ED] p-3 rounded-lg border border-[#EAE5D9] leading-relaxed">
                    {candidate.summary}
                  </p>
                </div>
              )}
            </div>
          </div>

        </div>
      )}

    </div>
  );
}

// ----------------------------------------------------
// VIEW 3: Jobs + Apply & Matched Jobs (Job Seeker View)
// ----------------------------------------------------
function JobSeekerJobsApplyView({ candidate, jobs, appliedJobIds, onApply, onNavigateToResume }) {
  const [filterMode, setFilterMode] = useState("all"); // "all" or "matched"
  const userSkillSet = useMemo(() => new Set((candidate?.skills || []).map(s => s.toLowerCase())), [candidate?.skills]);

  // Compute match for each company job using existing matching logic
  const jobsWithMatch = useMemo(() => {
    return jobs.map(job => {
      const reqSkills = job.required_skills || [];
      const matchedReq = reqSkills.filter(s => userSkillSet.has(s.toLowerCase()));
      const matchPct = reqSkills.length > 0 ? Math.round((matchedReq.length / reqSkills.length) * 100) : 100;
      const isApplied = appliedJobIds.has(job.id);
      return {
        ...job,
        matchedReq,
        matchPct,
        isApplied
      };
    });
  }, [jobs, userSkillSet, appliedJobIds]);

  const displayedJobs = useMemo(() => {
    if (filterMode === "matched") {
      return jobsWithMatch.filter(j => j.matchPct >= 60);
    }
    return jobsWithMatch;
  }, [jobsWithMatch, filterMode]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-heading text-[#2A2A2A]">Company Job Openings</h1>
          <p className="text-xs text-gray-600 mt-1">
            Browse active job requisitions from partner companies and submit your application with 1-click.
          </p>
        </div>

        {/* Filter Tabs: All vs Matched Only */}
        <div className="bg-[#F0ECE1] p-1 rounded-xl flex text-xs">
          <button
            onClick={() => setFilterMode("all")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${filterMode === "all" ? "bg-white text-[#2A2A2A] shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
          >
            All Openings ({jobsWithMatch.length})
          </button>
          <button
            onClick={() => setFilterMode("matched")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${filterMode === "matched" ? "bg-white text-[#2A2A2A] shadow-xs" : "text-gray-600 hover:text-gray-900"}`}
          >
            Matched Jobs ({jobsWithMatch.filter(j => j.matchPct >= 60).length})
          </button>
        </div>
      </div>

      {/* Jobs List */}
      {displayedJobs.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-[#EAE5D9] text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-[#F0ECE1] text-[#5E83AE] flex items-center justify-center text-2xl mx-auto">
            💼
          </div>
          <h3 className="text-base font-bold text-[#2A2A2A]">
            {filterMode === "matched" ? "No Matched Jobs Found" : "No Job Requisitions Available"}
          </h3>
          <p className="text-xs text-gray-500 max-w-sm mx-auto">
            {filterMode === "matched"
              ? "None of the active postings currently match at least 60% of your skills. Try uploading your resume to update your skill set."
              : "No companies have posted active job requisitions yet. Check back soon."}
          </p>
          {filterMode === "matched" && (
            <button
              onClick={onNavigateToResume}
              className="px-4 py-2 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-bold transition-smooth shadow-xs"
            >
              Update Resume & Skills →
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {displayedJobs.map((job) => (
            <div
              key={job.id}
              className="bg-white p-6 rounded-2xl border border-[#EAE5D9] card-hover flex flex-col justify-between space-y-4 shadow-sm"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-bold text-base text-[#2A2A2A]">{job.title}</h3>
                    <div className="text-xs text-gray-500 font-medium">{job.company_name} • {job.location}</div>
                  </div>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold shrink-0 ${job.matchPct >= 75 ? "bg-emerald-100 text-[#2E7D32]" : job.matchPct >= 60 ? "bg-blue-100 text-[#5E83AE]" : "bg-gray-100 text-gray-600"}`}>
                    {job.matchPct}% Skill Fit
                  </span>
                </div>

                <p className="text-xs text-gray-600 line-clamp-2">{job.description}</p>

                <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                  <span>💰 {job.salary_range}</span>
                  <span>•</span>
                  <span>⏳ {job.experience_required}</span>
                </div>

                {/* Required Skills */}
                <div className="pt-1">
                  <div className="text-[11px] font-semibold text-gray-500 mb-1.5">Required Skills:</div>
                  <div className="flex flex-wrap gap-1">
                    {job.required_skills?.map((s) => {
                      const hasSkill = userSkillSet.has(s.toLowerCase());
                      return (
                        <span
                          key={s}
                          className={`text-xs px-2 py-0.5 rounded-md font-medium border ${hasSkill ? "bg-[#E8F5E9] text-[#2E7D32] border-[#C8E6C9]" : "bg-[#F9F5ED] text-gray-600 border-[#EAE5D9]"}`}
                        >
                          {hasSkill ? "✓ " : ""}{s}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Action Button: Apply vs Already Applied */}
              <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[11px] text-gray-500">Posted on {job.created_at}</span>
                {job.isApplied ? (
                  <span className="px-4 py-1.5 rounded-xl bg-emerald-50 text-[#2E7D32] border border-emerald-200 text-xs font-bold inline-flex items-center gap-1">
                    <span>✓</span> Applied
                  </span>
                ) : (
                  <button
                    onClick={() => onApply(job.id)}
                    className="px-5 py-2 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-bold transition-smooth shadow-xs"
                  >
                    Apply Now →
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------
// VIEW 4: Recommended Roles (Strict Current-Skills Only)
// ----------------------------------------------------
function RecommendedRolesView({ candidate, recommendations, onAnalyzeGap, onGenerateRoadmap, onNavigateToResume }) {
  if (!candidate) return null;

  const [filterLevel, setFilterLevel] = useState("all");
  const hasSkills = candidate.skills && candidate.skills.length > 0;
  const roles = recommendations?.recommendations || [];

  const filteredRoles = useMemo(() => {
    if (filterLevel === "all") return roles;
    return roles.filter(r => r.level.toLowerCase().includes(filterLevel.toLowerCase()));
  }, [roles, filterLevel]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-100 text-[#2E7D32] text-xs font-bold mb-2">
            <span>✓</span> CURRENT-SKILL QUALIFICATION MATCHING
          </div>
          <h1 className="text-2xl font-bold font-heading text-[#2A2A2A]">Recommended Roles for Your Current Skills</h1>
          <p className="text-xs text-gray-600 mt-1 max-w-2xl">
            These roles are evaluated <strong>strictly against skills you currently have on file</strong>.
          </p>
        </div>

        {/* Filter */}
        {hasSkills && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 font-medium">Seniority:</span>
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-lg px-3 py-1.5 font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            >
              <option value="all">All Seniority Levels</option>
              <option value="Mid">Mid-Level</option>
              <option value="Senior">Senior</option>
              <option value="Lead">Lead / Architect</option>
            </select>
          </div>
        )}
      </div>

      {/* Empty State if no skills on profile */}
      {!hasSkills ? (
        <div className="bg-white p-12 rounded-2xl border border-[#EAE5D9] text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-[#F0ECE1] text-[#5E83AE] flex items-center justify-center text-2xl mx-auto">
            📄
          </div>
          <h3 className="text-base font-bold text-[#2A2A2A]">No Skills on File Yet</h3>
          <p className="text-xs text-gray-500 max-w-md mx-auto">
            Upload your resume or add your skills in the Resume & Skills section to discover roles you qualify for immediately.
          </p>
          <button
            onClick={onNavigateToResume}
            className="px-5 py-2.5 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-bold transition-smooth shadow-sm"
          >
            Go to Resume & Skills →
          </button>
        </div>
      ) : (
        /* Roles List */
        <div className="space-y-5">
          {filteredRoles.map((role) => {
            const isHighMatch = role.match_percentage >= 75;
            return (
              <div
                key={role.role_id}
                className="bg-white rounded-2xl p-6 border border-[#EAE5D9] card-hover space-y-4"
              >
                {/* Card Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h2 className="text-xl font-bold text-[#2A2A2A]">{role.title}</h2>
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#F0ECE1] text-[#2A2A2A] font-semibold">
                        {role.level}
                      </span>
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-50 text-[#5E83AE] font-semibold border border-blue-100">
                        {role.category}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">{role.description}</p>
                  </div>

                  {/* Match Percentage */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center shrink-0">
                    <div className={`text-xl font-bold ${isHighMatch ? "text-[#2E7D32]" : "text-[#5E83AE]"}`}>
                      {role.match_percentage}% Match
                    </div>
                    <div className="text-xs font-bold text-gray-700">{role.salary_range}</div>
                  </div>
                </div>

                {/* Match Progress Bar */}
                <div className="w-full bg-[#F0ECE1] h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${isHighMatch ? "bg-[#2E7D32]" : "bg-[#5E83AE]"}`}
                    style={{ width: `${role.match_percentage}%` }}
                  ></div>
                </div>

                {/* Skills Analysis Breakdown */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  
                  {/* Matched Required Skills */}
                  <div className="bg-[#F9F5ED] p-3.5 rounded-xl border border-[#EAE5D9]">
                    <div className="text-xs font-bold text-[#2E7D32] mb-2 flex items-center gap-1">
                      <span>✓</span> Matched Skills You Have ({role.matched_required_skills.length})
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {role.matched_required_skills.length === 0 ? (
                        <span className="text-xs text-gray-400">None yet</span>
                      ) : (
                        role.matched_required_skills.map((s) => (
                          <span key={s} className="text-xs px-2 py-0.5 rounded-md bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-medium">
                            {s}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Optional Bonus Skills */}
                  <div className="bg-[#F9F5ED] p-3.5 rounded-xl border border-[#EAE5D9]">
                    <div className="text-xs font-bold text-gray-700 mb-2 flex items-center gap-1">
                      <span>⚡</span> Nice-to-Have Additional Skills
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {role.matched_preferred_skills.map((s) => (
                        <span key={s} className="text-xs px-2 py-0.5 rounded-md bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-medium">
                          ✓ {s} (Have)
                        </span>
                      ))}
                      {role.missing_preferred_skills.map((s) => (
                        <span key={s} className="text-xs px-2 py-0.5 rounded-md bg-white text-gray-600 border border-gray-200 font-medium">
                          + {s} (Optional)
                        </span>
                      ))}
                    </div>
                  </div>

                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100">
                  <span className="text-xs text-gray-500">
                    Career Progression: {role.future_role_paths?.join(" → ") || "Specialization"}
                  </span>

                  <div className="flex gap-3">
                    <button
                      onClick={() => onAnalyzeGap(role.role_id)}
                      className="px-4 py-2 rounded-xl bg-[#F0ECE1] hover:bg-[#EAE5D9] text-[#2A2A2A] text-xs font-bold transition-smooth"
                    >
                      Analyze Skill Gap
                    </button>
                    <button
                      onClick={() => onGenerateRoadmap(role.role_id)}
                      className="px-4 py-2 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-bold transition-smooth shadow-sm"
                    >
                      Personalized Roadmap →
                    </button>
                  </div>
                </div>

              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------
// VIEW 5: Role Details & Skill Gap Analysis
// ----------------------------------------------------
function RoleDetailsSkillGapView({ gapData, candidate, onGenerateRoadmap, onBack, onSelectAnotherRole }) {
  if (!gapData || !candidate) return null;

  const targetRole = gapData.target_role;
  const gaps = gapData.gap_breakdown || [];

  return (
    <div className="space-y-8">
      {/* Back Button & Header */}
      <div>
        <button
          onClick={onBack}
          className="text-xs font-semibold text-[#5E83AE] hover:underline mb-3 inline-flex items-center gap-1"
        >
          ← Back to Recommended Roles
        </button>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold font-heading text-[#2A2A2A]">
              Skill Gap Analysis: {targetRole?.title}
            </h1>
            <p className="text-xs text-gray-600 mt-1">
              Comparing your verified current skills against the target role requirements to identify growth opportunities.
            </p>
          </div>

          <button
            onClick={() => onGenerateRoadmap(targetRole?.id)}
            className="px-5 py-2.5 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-bold transition-smooth shadow"
          >
            Generate Learning Roadmap →
          </button>
        </div>
      </div>

      {/* Role Overview & Impact Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-xl border border-[#EAE5D9] shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Current Readiness</div>
          <div className="text-3xl font-bold text-[#5E83AE]">{gapData.current_readiness_pct}%</div>
          <p className="text-xs text-gray-500 mt-1">Based on shared competencies</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#EAE5D9] shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Target Compensation</div>
          <div className="text-2xl font-bold text-[#2E7D32]">{gapData.career_impact?.salary_potential}</div>
          <p className="text-xs text-gray-500 mt-1">Seniority: {gapData.career_impact?.seniority_level}</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#EAE5D9] shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Estimated Learning Path</div>
          <div className="text-3xl font-bold text-[#2A2A2A]">{gapData.estimated_total_learning_weeks} Weeks</div>
          <p className="text-xs text-gray-500 mt-1">{gapData.missing_skills_count} skill gaps to bridge</p>
        </div>
      </div>

      {/* Side-by-Side: Foundation Skills You Have vs Missing Skills to Acquire */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Foundation Skills You Have */}
        <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#2E7D32] flex items-center gap-1.5">
              <span>✓</span> Foundation Skills You Already Have ({gapData.matched_skills?.length || 0})
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-100 text-[#2E7D32] font-semibold">
              Transferable
            </span>
          </div>
          <p className="text-xs text-gray-600">
            These skills transfer directly to {targetRole?.title}:
          </p>

          <div className="flex flex-wrap gap-2">
            {gapData.matched_skills && gapData.matched_skills.length > 0 ? (
              gapData.matched_skills.map((s) => (
                <span key={s} className="text-xs px-3 py-1.5 rounded-lg bg-[#E8F5E9] text-[#2E7D32] font-semibold border border-[#C8E6C9]">
                  ✓ {s}
                </span>
              ))
            ) : (
              <span className="text-xs text-gray-400">No overlapping skills yet.</span>
            )}
          </div>
        </div>

        {/* Missing Skills Gap */}
        <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#B45309] flex items-center gap-1.5">
              <span>⚡</span> Skills to Unlock This Role ({gapData.missing_skills_count || 0})
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-100 text-[#B45309] font-semibold">
              Target Gap
            </span>
          </div>
          <p className="text-xs text-gray-600">
            Acquiring these skills bridges the requirement gap for {targetRole?.title}:
          </p>

          <div className="flex flex-wrap gap-2">
            {gaps.map((g) => (
              <span key={g.skill} className="text-xs px-3 py-1.5 rounded-lg bg-[#FEF3C7] text-[#B45309] font-semibold border border-[#FDE68A]">
                + {g.skill} ({g.est_weeks} wks)
              </span>
            ))}
          </div>
        </div>

      </div>

      {/* Detailed Skill Breakdown */}
      <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-6">
        <h2 className="text-lg font-bold text-[#2A2A2A]">Detailed Skill Breakdown & Suggestions</h2>

        <div className="space-y-4">
          {gaps.map((gap, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#F9F5ED] border border-[#EAE5D9] space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-[#2A2A2A]">{gap.skill}</span>
                  <span className={`text-[11px] px-2 py-0.5 rounded-md font-semibold ${gap.is_core ? "bg-red-100 text-red-700" : "bg-blue-100 text-[#5E83AE]"}`}>
                    {gap.importance}
                  </span>
                </div>
                <div className="text-xs font-semibold text-gray-600">
                  Est. Effort: {gap.est_weeks} Weeks • Difficulty: {gap.difficulty}
                </div>
              </div>

              <p className="text-xs text-gray-700 leading-relaxed">{gap.summary}</p>
              
              {gap.project_idea && (
                <div className="text-xs bg-white p-2.5 rounded-lg border border-[#EAE5D9] text-gray-800">
                  <span className="font-bold text-[#5E83AE]">Suggested Project: </span>
                  {gap.project_idea}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// VIEW 6: Future Opportunities & Learning Roadmap
// ----------------------------------------------------
function LearningRoadmapView({ roadmap, candidate, onBack, showToast }) {
  if (!roadmap || !candidate) return null;

  const [completedTasks, setCompletedTasks] = useState({});

  const toggleTask = (phaseIdx, taskIdx) => {
    const key = `${phaseIdx}-${taskIdx}`;
    setCompletedTasks(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <button
          onClick={onBack}
          className="text-xs font-semibold text-[#5E83AE] hover:underline mb-3 inline-flex items-center gap-1"
        >
          ← Back to Skill Gap Analysis
        </button>
        <div className="bg-[#2A2A2A] rounded-2xl p-6 text-white flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
          <div>
            <div className="text-xs text-[#A6C4E5] font-semibold uppercase tracking-wider mb-1">
              Personalized Learning Roadmap
            </div>
            <h1 className="text-2xl font-bold font-heading">
              {roadmap.target_role_title} Progression Plan
            </h1>
            <p className="text-xs text-gray-300 mt-1">
              Structured {roadmap.total_estimated_weeks}-week progression roadmap designed to build your skills.
            </p>
          </div>

          <div className="text-left md:text-right shrink-0">
            <div className="text-xs text-gray-400">Target Level & Salary</div>
            <div className="text-lg font-bold text-emerald-400">{roadmap.target_role_salary}</div>
          </div>
        </div>
      </div>

      {/* Progression Phases Timeline */}
      <div className="space-y-6">
        {roadmap.learning_modules?.map((mod, pIdx) => (
          <div key={pIdx} className="bg-white rounded-2xl p-6 border border-[#EAE5D9] shadow-sm space-y-4">
            
            {/* Module Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-100 pb-3">
              <div className="space-y-1">
                <span className="text-xs font-bold text-[#5E83AE] uppercase tracking-wider">{mod.weeks}</span>
                <h3 className="text-lg font-bold text-[#2A2A2A]">{mod.phase}</h3>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {mod.focus_skills?.map((s) => (
                  <span key={s} className="text-xs px-2.5 py-0.5 rounded-full bg-[#F0ECE1] text-[#2A2A2A] font-semibold">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <p className="text-xs text-gray-700 leading-relaxed">{mod.description}</p>

            {/* Tasks Checklist */}
            {mod.tasks && mod.tasks.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-bold text-gray-600 uppercase tracking-wider">Milestone Action Items:</div>
                <div className="space-y-1.5">
                  {mod.tasks.map((task, tIdx) => {
                    const isDone = !!completedTasks[`${pIdx}-${tIdx}`];
                    return (
                      <div
                        key={tIdx}
                        onClick={() => toggleTask(pIdx, tIdx)}
                        className={`flex items-start gap-2.5 p-2.5 rounded-lg border text-xs cursor-pointer transition-smooth ${isDone ? "bg-emerald-50 border-emerald-200 text-emerald-900" : "bg-[#F9F5ED] border-[#EAE5D9] text-gray-800 hover:bg-[#F3EFE6]"}`}
                      >
                        <input
                          type="checkbox"
                          checked={isDone}
                          onChange={() => {}}
                          className="mt-0.5 rounded text-[#5E83AE] focus:ring-[#5E83AE]"
                        />
                        <span className={isDone ? "line-through opacity-75" : ""}>{task}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Project Blueprint */}
            {mod.project && (
              <div className="p-3.5 rounded-xl bg-blue-50/50 border border-blue-100 text-xs space-y-1">
                <div className="font-bold text-[#5E83AE] flex items-center gap-1">
                  <span>🛠️</span> Suggested Project Milestone
                </div>
                <p className="text-gray-700">{mod.project}</p>
              </div>
            )}

            {/* Curated Resources */}
            {mod.resources && mod.resources.length > 0 && (
              <div className="pt-2">
                <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Learning Resources:</div>
                <div className="flex flex-wrap gap-2">
                  {mod.resources.map((res, rIdx) => (
                    <a
                      key={rIdx}
                      href={res.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs px-3 py-1 rounded-lg bg-white border border-[#D5CEBF] hover:border-[#5E83AE] text-[#5E83AE] font-semibold transition-smooth inline-flex items-center gap-1 shadow-2xs"
                    >
                      <span>{res.title}</span>
                      <span className="text-[10px] text-gray-400">({res.type}) ↗</span>
                    </a>
                  ))}
                </div>
              </div>
            )}

          </div>
        ))}
      </div>
    </div>
  );
}

// ----------------------------------------------------
// VIEW 7: Company Dashboard with Edit & Delete Requisitions
// ----------------------------------------------------
function CompanyDashboardView({ company, jobs, onCreateJob, onEditJob, onDeleteJob, onViewMatches }) {
  if (!company) return null;

  const [deleteTargetId, setDeleteTargetId] = useState(null);
  const totalMatches = jobs.reduce((acc, j) => acc + (j.matched_candidates_count || 0), 0);
  const totalHighFit = jobs.reduce((acc, j) => acc + (j.high_fit_candidates_count || 0), 0);

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-[#2A2A2A] rounded-2xl p-6 sm:p-8 text-white relative overflow-hidden shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#5E83AE]/30 text-[#A6C4E5] text-xs font-semibold border border-[#5E83AE]/40">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Recruiter Workspace
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-heading">
            {company.name} Talent Console
          </h1>
          <p className="text-gray-300 text-sm leading-relaxed">
            {company.description || "Manage your job requisitions and review candidates matched by required skills."}
          </p>
        </div>

        <button
          onClick={onCreateJob}
          className="px-5 py-3 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white font-bold text-sm transition-smooth shadow shrink-0 self-start md:self-auto"
        >
          + Post Job Requisition
        </button>
      </div>

      {/* Delete Job Confirmation Modal */}
      <ConfirmModal
        isOpen={!!deleteTargetId}
        title="Delete Job Requisition"
        message="Are you sure you want to delete this job requisition? All applicant matching data for this post will be removed. This action cannot be undone."
        confirmText="Delete Requisition"
        confirmColor="bg-red-600 hover:bg-red-700"
        onConfirm={() => {
          onDeleteJob(deleteTargetId);
          setDeleteTargetId(null);
        }}
        onCancel={() => setDeleteTargetId(null)}
      />

      {/* Company Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-xl border border-[#EAE5D9] shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Active Postings</div>
          <div className="text-3xl font-bold text-[#2A2A2A]">{jobs.length}</div>
          <p className="text-xs text-gray-500 mt-1">Open hiring requisitions</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#EAE5D9] shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Candidates Evaluated</div>
          <div className="text-3xl font-bold text-[#5E83AE]">{totalMatches}</div>
          <p className="text-xs text-gray-500 mt-1">Across all postings</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-[#EAE5D9] shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">High-Fit Candidates</div>
          <div className="text-3xl font-bold text-[#2E7D32]">{totalHighFit}</div>
          <p className="text-xs text-gray-500 mt-1">Matching 60%+ of required skills</p>
        </div>
      </div>

      {/* Active Job Requisitions List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[#2A2A2A]">Your Job Requisitions</h2>
          <button
            onClick={onCreateJob}
            className="text-xs font-semibold text-[#5E83AE] hover:underline"
          >
            + Create New Post
          </button>
        </div>

        {jobs.length === 0 ? (
          <div className="bg-white p-12 rounded-2xl text-center border border-[#EAE5D9] space-y-3">
            <div className="w-12 h-12 rounded-full bg-[#F0ECE1] text-[#5E83AE] flex items-center justify-center text-2xl mx-auto">
              💼
            </div>
            <h3 className="text-base font-bold text-[#2A2A2A]">No Job Requisitions Yet</h3>
            <p className="text-xs text-gray-500 max-w-sm mx-auto">
              Create your first job posting to match against registered candidates.
            </p>
            <button
              onClick={onCreateJob}
              className="px-5 py-2.5 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-bold transition-smooth shadow-sm"
            >
              + Post Job Requisition
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="bg-white p-6 rounded-2xl border border-[#EAE5D9] card-hover flex flex-col justify-between space-y-4 shadow-sm relative group"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="pr-12">
                      <h3 className="font-bold text-base text-[#2A2A2A]">{job.title}</h3>
                      <span className="text-xs font-semibold text-[#5E83AE] bg-blue-50 px-2 py-0.5 rounded-full inline-block mt-1">
                        {job.location}
                      </span>
                    </div>

                    {/* Small Edit and Delete Icons */}
                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        onClick={() => onEditJob(job)}
                        className="p-1.5 rounded-lg bg-[#F0ECE1] hover:bg-[#E2DDD0] text-[#2A2A2A] text-xs font-bold transition-smooth"
                        title="Edit Job Requisition"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => setDeleteTargetId(job.id)}
                        className="p-1.5 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 text-xs font-bold transition-smooth"
                        title="Delete Job Requisition"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  <p className="text-xs text-gray-600 line-clamp-2">{job.description}</p>
                  
                  {/* Required Skills */}
                  <div className="pt-1">
                    <div className="text-[11px] font-semibold text-gray-500 mb-1">Required Skills:</div>
                    <div className="flex flex-wrap gap-1">
                      {job.required_skills?.map((s) => (
                        <span key={s} className="text-[11px] px-2 py-0.5 rounded-md bg-[#F0ECE1] text-[#2A2A2A] font-medium border border-[#E2DDD0]">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
                  <div className="text-xs">
                    <span className="font-bold text-[#2E7D32]">{job.high_fit_candidates_count || 0}</span>
                    <span className="text-gray-500 ml-1">High-Fit Candidates</span>
                  </div>

                  <button
                    onClick={() => onViewMatches(job.id)}
                    className="px-4 py-1.5 rounded-lg bg-[#2A2A2A] hover:bg-[#3D4A59] text-white text-xs font-semibold transition-smooth"
                  >
                    View Candidates →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ----------------------------------------------------
// EDIT JOB MODAL
// ----------------------------------------------------
function EditJobModal({ job, onClose, onSave }) {
  const [title, setTitle] = useState(job.title || "");
  const [description, setDescription] = useState(job.description || "");
  const [location, setLocation] = useState(job.location || "Remote");
  const [experienceRequired, setExperienceRequired] = useState(job.experience_required || "2+ years");
  const [salaryRange, setSalaryRange] = useState(job.salary_range || "$95,000 - $135,000");
  const [requiredSkills, setRequiredSkills] = useState(job.required_skills || []);
  const [preferredSkills, setPreferredSkills] = useState(job.preferred_skills || []);
  const [customSkillInput, setCustomSkillInput] = useState("");

  const addSkill = () => {
    if (!customSkillInput.trim()) return;
    if (!requiredSkills.includes(customSkillInput.trim())) {
      setRequiredSkills([...requiredSkills, customSkillInput.trim()]);
      setCustomSkillInput("");
    }
  };

  const removeSkill = (s) => {
    setRequiredSkills(requiredSkills.filter(sk => sk !== s));
  };

  const handleSave = (e) => {
    e.preventDefault();
    onSave(job.id, {
      title,
      description,
      location,
      experience_required: experienceRequired,
      salary_range: salaryRange,
      required_skills: requiredSkills,
      preferred_skills: preferredSkills
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl p-6 max-w-2xl w-full border border-[#EAE5D9] shadow-xl space-y-4 my-8">
        <div className="flex items-center justify-between border-b border-gray-100 pb-3">
          <h3 className="font-bold text-lg text-[#2A2A2A]">Edit Job Requisition</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 font-bold text-lg">×</button>
        </div>

        <form onSubmit={handleSave} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Job Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
              />
            </div>
            <div>
              <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Experience Required</label>
              <input
                type="text"
                value={experienceRequired}
                onChange={(e) => setExperienceRequired(e.target.value)}
                className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
              />
            </div>
            <div>
              <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Salary Range</label>
              <input
                type="text"
                value={salaryRange}
                onChange={(e) => setSalaryRange(e.target.value)}
                className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
              />
            </div>
          </div>

          <div>
            <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Job Description *</label>
            <textarea
              required
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl p-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            ></textarea>
          </div>

          {/* Required Skills */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="font-bold text-gray-700 uppercase tracking-wider">Required Skills ({requiredSkills.length})</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Add skill..."
                  value={customSkillInput}
                  onChange={(e) => setCustomSkillInput(e.target.value)}
                  className="bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-lg px-2 py-1"
                />
                <button
                  type="button"
                  onClick={addSkill}
                  className="px-2.5 py-1 rounded-lg bg-[#2A2A2A] text-white text-xs font-semibold"
                >
                  + Add
                </button>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5 p-2.5 rounded-xl bg-[#F9F5ED] border border-[#EAE5D9]">
              {requiredSkills.map((s) => (
                <span key={s} className="px-2.5 py-1 rounded-lg bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-semibold flex items-center gap-1">
                  <span>{s}</span>
                  <button type="button" onClick={() => removeSkill(s)} className="text-gray-400 hover:text-red-600 ml-1">×</button>
                </span>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white font-bold shadow-xs"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// INTERVIEW SELECTION MODAL
// ----------------------------------------------------
function InterviewSelectionModal({ candidate, job, onClose, onSubmit }) {
  const [location, setLocation] = useState("Google Meet (Video Conference)");
  const [date, setDate] = useState(() => {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);
    return nextWeek.toISOString().split("T")[0];
  });
  const [time, setTime] = useState("10:00 AM EST");
  const [requiredDocuments, setRequiredDocuments] = useState("Resume, Portfolio / GitHub links, Government ID");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      status: "interview",
      location,
      date,
      time,
      required_documents: requiredDocuments
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl p-6 max-w-lg w-full border border-[#EAE5D9] shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-gray-100 pb-3">
          <div>
            <h3 className="font-bold text-base text-[#2A2A2A]">Select for Interview</h3>
            <p className="text-xs text-gray-500">Candidate: <strong>{candidate.name}</strong> • Role: <strong>{job.title}</strong></p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 font-bold text-lg">×</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
          <div>
            <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Interview Location / Platform *</label>
            <input
              type="text"
              required
              placeholder="e.g. Google Meet / Office Room 3B"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Interview Date *</label>
              <input
                type="date"
                required
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
              />
            </div>
            <div>
              <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Interview Time *</label>
              <input
                type="text"
                required
                placeholder="e.g. 10:30 AM EST"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl px-3 py-2 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
              />
            </div>
          </div>

          <div>
            <label className="block font-bold text-gray-700 uppercase tracking-wider mb-1">Required Documents *</label>
            <textarea
              required
              rows={2}
              placeholder="List required documents (e.g. Identification, Portfolio links, Degree certificates)..."
              value={requiredDocuments}
              onChange={(e) => setRequiredDocuments(e.target.value)}
              className="w-full bg-[#F9F5ED] border border-[#D5CEBF] rounded-xl p-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            ></textarea>
          </div>

          <div className="p-3 bg-blue-50/70 border border-blue-100 rounded-xl text-[11px] text-gray-700 space-y-1">
            <span className="font-bold text-[#5E83AE]">Structured Notification:</span>
            <p>A formal interview invitation with the schedule and instructions will be sent directly to the candidate.</p>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-[#2E7D32] hover:bg-[#256628] text-white font-bold shadow-xs"
            >
              Send Interview Invitation →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// NOTIFICATIONS MODAL (Job Seeker View)
// ----------------------------------------------------
function NotificationsModal({ notifications, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl p-6 max-w-lg w-full border border-[#EAE5D9] shadow-xl space-y-4 max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between border-b border-gray-100 pb-3 shrink-0">
          <h3 className="font-bold text-base text-[#2A2A2A] flex items-center gap-2">
            <span>🔔</span> Notifications & Status Updates ({notifications.length})
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 font-bold text-lg">×</button>
        </div>

        <div className="overflow-y-auto space-y-3 flex-1 pr-1">
          {notifications.length === 0 ? (
            <div className="p-8 text-center text-xs text-gray-500">
              No notifications yet. When companies schedule interviews or update your applications, they will appear here.
            </div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`p-4 rounded-xl border text-xs space-y-2 ${n.type === "interview_invitation" ? "bg-emerald-50/60 border-emerald-200" : "bg-[#F9F5ED] border-[#EAE5D9]"}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-bold text-sm text-[#2A2A2A]">{n.title}</h4>
                  <span className="text-[10px] text-gray-500 shrink-0">{n.created_at}</span>
                </div>

                {n.type === "interview_invitation" ? (
                  <div className="space-y-1.5 pt-1 text-gray-700">
                    <div><strong>📍 Location:</strong> {n.location}</div>
                    <div><strong>📅 Date:</strong> {n.date} • <strong>⏰ Time:</strong> {n.time}</div>
                    <div><strong>📋 Required Documents:</strong> {n.required_documents}</div>
                  </div>
                ) : (
                  <p className="text-gray-700 leading-relaxed pt-1">{n.message}</p>
                )}
              </div>
            ))
          )}
        </div>

        <div className="pt-2 border-t border-gray-100 text-right shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-[#2A2A2A] text-white text-xs font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------
// VIEW 8: Create Job Requisition
// ----------------------------------------------------
function CreateJobView({ company, onJobCreated, onCancel, showToast }) {
  if (!company) return null;

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("Remote");
  const [experienceRequired, setExperienceRequired] = useState("2+ years");
  const [salaryRange, setSalaryRange] = useState("$95,000 - $135,000");
  const [requiredSkills, setRequiredSkills] = useState([]);
  const [preferredSkills, setPreferredSkills] = useState([]);
  const [customSkillInput, setCustomSkillInput] = useState("");
  const [isExtracting, setIsExtracting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Auto-Detect Skills from Job Description
  const handleExtractFromDescription = async () => {
    if (!description.trim()) {
      showToast("Please enter a job description first.", "info");
      return;
    }
    setIsExtracting(true);
    try {
      const res = await fetch(`${API_BASE}/jobs/extract-skills`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: description })
      });
      const data = await res.json();
      const skills = data.skills || [];
      if (skills.length > 0) {
        setRequiredSkills(skills.slice(0, 5));
        setPreferredSkills(skills.slice(5, 10));
        showToast(`${skills.length} skills identified from description!`, "success");
      } else {
        showToast("No standardized skills identified. You can add them manually.", "info");
      }
    } catch (e) {
      showToast("Error identifying skills from description.", "error");
    } finally {
      setIsExtracting(false);
    }
  };

  const addRequiredSkill = () => {
    if (!customSkillInput.trim()) return;
    if (!requiredSkills.includes(customSkillInput.trim())) {
      setRequiredSkills([...requiredSkills, customSkillInput.trim()]);
      setCustomSkillInput("");
    }
  };

  const removeRequiredSkill = (skill) => {
    setRequiredSkills(requiredSkills.filter(s => s !== skill));
  };

  const removePreferredSkill = (skill) => {
    setPreferredSkills(preferredSkills.filter(s => s !== skill));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      showToast("Please fill in Title and Description.", "error");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_id: company.id,
          title,
          description,
          location,
          experience_required: experienceRequired,
          salary_range: salaryRange,
          required_skills: requiredSkills,
          preferred_skills: preferredSkills
        })
      });
      const data = await res.json();
      if (data.success && data.job) {
        onJobCreated(data.job);
      } else {
        showToast("Failed to create job requisition.", "error");
      }
    } catch (e) {
      showToast("Error submitting job.", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-heading text-[#2A2A2A]">Create Job Requisition</h1>
          <p className="text-xs text-gray-600 mt-1">Post a new role for {company.name} and match candidates automatically.</p>
        </div>
        <button onClick={onCancel} className="text-xs font-semibold text-gray-500 hover:text-gray-800">
          Cancel
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-6 sm:p-8 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-5">
        
        {/* Job Title & Location */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Job Title *</label>
            <input
              type="text"
              required
              placeholder="e.g. Frontend Engineer"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Location</label>
            <input
              type="text"
              placeholder="e.g. San Francisco, CA (Remote)"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            />
          </div>
        </div>

        {/* Experience & Salary */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Experience Required</label>
            <input
              type="text"
              placeholder="e.g. 3+ years"
              value={experienceRequired}
              onChange={(e) => setExperienceRequired(e.target.value)}
              className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">Salary Range</label>
            <input
              type="text"
              placeholder="e.g. $110,000 - $145,000"
              value={salaryRange}
              onChange={(e) => setSalaryRange(e.target.value)}
              className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl px-3.5 py-2.5 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE]"
            />
          </div>
        </div>

        {/* Description & Auto-Detect Button */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider">Job Description *</label>
            <button
              type="button"
              onClick={handleExtractFromDescription}
              disabled={isExtracting}
              className="text-xs px-2.5 py-1 rounded-lg bg-[#5E83AE]/10 hover:bg-[#5E83AE]/20 text-[#5E83AE] font-bold transition-smooth"
            >
              {isExtracting ? "Detecting..." : "⚡ Auto-Detect Skills from Text"}
            </button>
          </div>
          <textarea
            required
            rows={4}
            placeholder="Describe key responsibilities and required skills (e.g. React, TypeScript, Docker, AWS, RESTful APIs)..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-xl p-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#5E83AE] leading-relaxed"
          ></textarea>
        </div>

        {/* Required Skills Tagging */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider">Required Skills ({requiredSkills.length})</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Add skill..."
                value={customSkillInput}
                onChange={(e) => setCustomSkillInput(e.target.value)}
                className="bg-[#F9F5ED] border border-[#D5CEBF] text-xs rounded-lg px-2.5 py-1 text-gray-800"
              />
              <button
                type="button"
                onClick={addRequiredSkill}
                className="px-2.5 py-1 rounded-lg bg-[#2A2A2A] text-white text-xs font-semibold"
              >
                + Add
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5 p-3 rounded-xl bg-[#F9F5ED] border border-[#EAE5D9] min-h-[44px]">
            {requiredSkills.length === 0 ? (
              <span className="text-xs text-gray-400">No required skills specified yet. Type above or click Auto-Detect Skills.</span>
            ) : (
              requiredSkills.map((s) => (
                <span key={s} className="text-xs px-2.5 py-1 rounded-lg bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-semibold flex items-center gap-1">
                  <span>{s}</span>
                  <button type="button" onClick={() => removeRequiredSkill(s)} className="text-gray-400 hover:text-red-600 font-bold ml-1">×</button>
                </span>
              ))
            )}
          </div>
        </div>

        {/* Preferred Skills Tagging */}
        {preferredSkills.length > 0 && (
          <div className="space-y-2">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider">Preferred / Bonus Skills ({preferredSkills.length})</label>
            <div className="flex flex-wrap gap-1.5 p-3 rounded-xl bg-[#F9F5ED] border border-[#EAE5D9]">
              {preferredSkills.map((s) => (
                <span key={s} className="text-xs px-2.5 py-1 rounded-lg bg-blue-50 text-[#5E83AE] border border-blue-200 font-semibold flex items-center gap-1">
                  <span>{s}</span>
                  <button type="button" onClick={() => removePreferredSkill(s)} className="text-gray-400 hover:text-red-600 font-bold ml-1">×</button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
          <button
            type="button"
            onClick={onCancel}
            className="px-5 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold transition-smooth"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2.5 rounded-xl bg-[#5E83AE] hover:bg-[#4A6B8F] text-white text-xs font-bold transition-smooth shadow"
          >
            {isSubmitting ? "Publishing..." : "Publish Job Requisition"}
          </button>
        </div>

      </form>
    </div>
  );
}

// ----------------------------------------------------
// VIEW 9: Matched Candidates with Interview & Rejection
// ----------------------------------------------------
function MatchedCandidatesView({ matchData, onSelectInterview, onRejectCandidate, onViewCandidate, onBack }) {
  if (!matchData) return null;

  const job = matchData.job;
  const candidates = matchData.matched_candidates || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <button
          onClick={onBack}
          className="text-xs font-semibold text-[#5E83AE] hover:underline mb-3 inline-flex items-center gap-1"
        >
          ← Back to Company Dashboard
        </button>
        <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="text-xs text-[#5E83AE] font-bold uppercase tracking-wider mb-1">
              Candidate Skill Matching
            </div>
            <h1 className="text-2xl font-bold font-heading text-[#2A2A2A]">
              Matched Candidates for: {job?.title}
            </h1>
            <p className="text-xs text-gray-600 mt-1">
              Candidates ranked by skill match against required competencies. Select candidates for interview or manage application status.
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs px-3 py-1 rounded-full bg-emerald-100 text-[#2E7D32] font-bold">
              {candidates.filter(c => c.match_score >= 60).length} High-Fit Matches
            </span>
          </div>
        </div>
      </div>

      {/* Empty State if no candidates registered or matched */}
      {candidates.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl border border-[#EAE5D9] text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-[#F0ECE1] text-[#5E83AE] flex items-center justify-center text-2xl mx-auto">
            👥
          </div>
          <h3 className="text-base font-bold text-[#2A2A2A]">No Candidates Registered Yet</h3>
          <p className="text-xs text-gray-500 max-w-sm mx-auto">
            As job seekers register and upload their resumes, they will automatically be evaluated and ranked here.
          </p>
        </div>
      ) : (
        /* Ranked Candidate Cards List */
        <div className="space-y-4">
          {candidates.map((cand, rankIdx) => {
            const isTopFit = cand.match_score >= 75;
            const isBelow60 = cand.match_score < 60;
            const isInterview = cand.application_status === "interview";
            const isRejected = cand.application_status === "rejected";

            return (
              <div
                key={cand.candidate_id}
                className="bg-white rounded-2xl p-6 border border-[#EAE5D9] card-hover space-y-4"
              >
                {/* Card Top Row */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    {/* Rank Badge */}
                    <div className="w-9 h-9 rounded-xl bg-[#2A2A2A] text-white flex items-center justify-center font-bold text-sm shadow-sm">
                      #{rankIdx + 1}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-base text-[#2A2A2A]">{cand.name}</h3>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${isTopFit ? "bg-emerald-100 text-[#2E7D32]" : "bg-blue-100 text-[#5E83AE]"}`}>
                          {cand.tier}
                        </span>

                        {/* Status Badges */}
                        {isInterview && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-600 text-white font-bold">
                            ✓ Interview Scheduled
                          </span>
                        )}
                        {isRejected && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-semibold">
                            Not Selected
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500">{cand.title} • {cand.email}</p>
                    </div>
                  </div>

                  {/* Score Breakdown */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center shrink-0">
                    <div className={`text-2xl font-bold ${isTopFit ? "text-[#2E7D32]" : "text-[#5E83AE]"}`}>
                      {cand.match_score}% Match
                    </div>
                    <div className="text-[11px] text-gray-500 font-medium">
                      Required: {cand.req_match_percentage}% • Preferred: {cand.pref_match_percentage}%
                    </div>
                  </div>
                </div>

                {/* Interview Scheduled Banner if active */}
                {isInterview && cand.interview_details && (
                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-gray-800 space-y-1">
                    <div className="font-bold text-[#2E7D32] flex items-center gap-1.5">
                      <span>📅</span> Interview Scheduled
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-0.5">
                      <div><strong>Date & Time:</strong> {cand.interview_details.date} at {cand.interview_details.time}</div>
                      <div><strong>Location:</strong> {cand.interview_details.location}</div>
                      <div className="sm:col-span-2"><strong>Required Documents:</strong> {cand.interview_details.required_documents}</div>
                    </div>
                  </div>
                )}

                {/* Summary */}
                {cand.summary && (
                  <p className="text-xs text-gray-700 line-clamp-2 bg-[#F9F5ED] p-2.5 rounded-lg border border-[#EAE5D9]">
                    {cand.summary}
                  </p>
                )}

                {/* Skills Match Matrix */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                  {/* Matched Required */}
                  <div>
                    <div className="text-[11px] font-bold text-[#2E7D32] mb-1.5 flex items-center gap-1">
                      <span>✓</span> Matched Required Skills ({cand.matched_required_skills?.length || 0}):
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {cand.matched_required_skills?.length === 0 ? (
                        <span className="text-xs text-gray-400">None</span>
                      ) : (
                        cand.matched_required_skills?.map((s) => (
                          <span key={s} className="text-xs px-2 py-0.5 rounded-md bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] font-medium">
                            ✓ {s}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Missing Required */}
                  <div>
                    <div className="text-[11px] font-bold text-gray-500 mb-1.5 flex items-center gap-1">
                      <span>—</span> Missing Skills ({cand.missing_required_skills?.length || 0}):
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {cand.missing_required_skills?.length === 0 ? (
                        <span className="text-xs text-emerald-600 font-medium">All required skills matched!</span>
                      ) : (
                        cand.missing_required_skills?.map((s) => (
                          <span key={s} className="text-xs px-2 py-0.5 rounded-md bg-gray-100 text-gray-600 font-medium">
                            {s}
                          </span>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Footer Actions: Select Interview & Reject */}
                <div className="pt-3 border-t border-gray-100 flex flex-wrap items-center justify-between gap-3">
                  <button
                    onClick={() => onViewCandidate(cand.candidate_id)}
                    className="text-xs text-[#5E83AE] font-bold hover:underline"
                  >
                    View Full Dossier →
                  </button>

                  <div className="flex items-center gap-2">
                    {/* Select for Interview Button */}
                    <button
                      onClick={() => onSelectInterview(cand, job)}
                      className="px-4 py-2 rounded-xl bg-[#2E7D32] hover:bg-[#256628] text-white text-xs font-bold transition-smooth shadow-xs"
                    >
                      {isInterview ? "Update Interview" : "Select for Interview"}
                    </button>

                    {/* Reject Button */}
                    {!isRejected ? (
                      <button
                        onClick={() => onRejectCandidate(cand.candidate_id, job.id)}
                        className={`px-3 py-2 rounded-xl text-xs font-semibold transition-smooth ${isBelow60 ? "bg-red-50 hover:bg-red-100 text-red-700 border border-red-200" : "bg-gray-100 hover:bg-gray-200 text-gray-700"}`}
                        title={isBelow60 ? "Candidate below 60% match threshold" : "Reject application"}
                      >
                        {isBelow60 ? "Reject (<60% Match)" : "Reject"}
                      </button>
                    ) : (
                      <span className="text-xs text-gray-400 font-medium italic">Rejected</span>
                    )}
                  </div>
                </div>

              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------
// VIEW 10: Candidate Profile Dossier (Recruiter View)
// ----------------------------------------------------
function CandidateProfileView({ candidate, currentJob, onSelectInterview, onRejectCandidate, onBack }) {
  if (!candidate) return null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <button
          onClick={onBack}
          className="text-xs font-semibold text-[#5E83AE] hover:underline mb-3 inline-flex items-center gap-1"
        >
          ← Back to Matched Candidates
        </button>

        <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#2A2A2A] text-white flex items-center justify-center font-bold text-xl shadow-inner">
              {candidate.name?.split(" ").map(w => w[0]).join("") || "CD"}
            </div>
            <div>
              <h1 className="text-2xl font-bold font-heading text-[#2A2A2A]">{candidate.name}</h1>
              <p className="text-xs text-gray-600">{candidate.title} • {candidate.email} • {candidate.phone || "No phone listed"}</p>
              <div className="flex gap-3 text-xs text-[#5E83AE] font-semibold mt-1">
                {candidate.linkedin && <a href={candidate.linkedin} target="_blank" rel="noreferrer" className="hover:underline">LinkedIn ↗</a>}
                {candidate.github && <a href={candidate.github} target="_blank" rel="noreferrer" className="hover:underline">GitHub ↗</a>}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {currentJob && (
              <>
                <button
                  onClick={() => onSelectInterview(candidate, currentJob)}
                  className="px-4 py-2.5 rounded-xl bg-[#2E7D32] hover:bg-[#256628] text-white text-xs font-bold transition-smooth shadow-xs"
                >
                  Select for Interview
                </button>
                <button
                  onClick={() => onRejectCandidate(candidate.id, currentJob.id)}
                  className="px-3 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold transition-smooth"
                >
                  Reject
                </button>
              </>
            )}

            {candidate.resume_filename && (
              <a
                href={`${API_BASE}/resumes/file/${candidate.resume_filename}`}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2.5 rounded-xl bg-[#2A2A2A] hover:bg-[#3D4A59] text-white text-xs font-bold transition-smooth shadow-xs"
              >
                📄 View PDF Resume
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Summary */}
      {candidate.summary && (
        <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-2">
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Candidate Summary</h2>
          <p className="text-xs text-gray-700 leading-relaxed bg-[#F9F5ED] p-3.5 rounded-xl border border-[#EAE5D9]">
            {candidate.summary}
          </p>
        </div>
      )}

      {/* Verified Skills Matrix */}
      <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-3">
        <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider">
          Verified Skills ({candidate.skills?.length || 0})
        </h2>
        <div className="flex flex-wrap gap-2">
          {candidate.skills && candidate.skills.length > 0 ? (
            candidate.skills.map((s) => (
              <span key={s} className="text-xs px-3 py-1 rounded-lg bg-[#F0ECE1] text-[#2A2A2A] font-medium border border-[#E2DDD0]">
                {s}
              </span>
            ))
          ) : (
            <span className="text-xs text-gray-400">No skills listed yet.</span>
          )}
        </div>
      </div>

      {/* Experience & Education */}
      {(candidate.experience?.length > 0 || candidate.education?.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-4">
            <h2 className="font-bold text-[#2A2A2A] text-base">💼 Work Experience</h2>
            {candidate.experience && candidate.experience.length > 0 ? (
              <div className="space-y-4">
                {candidate.experience.map((exp, idx) => (
                  <div key={idx} className="border-l-2 border-[#5E83AE] pl-3 py-1 space-y-1">
                    <div className="font-bold text-xs text-[#2A2A2A]">{exp.title}</div>
                    <div className="text-[11px] text-[#5E83AE] font-medium">{exp.details}</div>
                    {exp.bullets && (
                      <ul className="text-xs text-gray-600 space-y-1 pt-1">
                        {exp.bullets.map((b, bIdx) => (
                          <li key={bIdx} className="list-disc ml-4">{b}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500">No work experience entries recorded.</p>
            )}
          </div>

          <div className="bg-white p-6 rounded-2xl border border-[#EAE5D9] shadow-sm space-y-4">
            <h2 className="font-bold text-[#2A2A2A] text-base">🎓 Education & Credentials</h2>
            {candidate.education && candidate.education.length > 0 ? (
              <div className="space-y-2">
                {candidate.education.map((edu, idx) => (
                  <div key={idx} className="text-xs font-medium text-gray-800 bg-[#F9F5ED] p-3 rounded-lg border border-[#EAE5D9]">
                    {edu.institution_or_degree}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500">No education entries recorded.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Render React App
const rootElement = document.getElementById("root");
ReactDOM.createRoot(rootElement).render(<App />);
