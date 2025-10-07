import React from "react";
import "./ProfileSummary.css";

const ProfileSummary = ({ data }) => {
  if (!data) return null;

  const {
    username,
    full_name,
    bio,
    followers_count,
    following_count,
    profile_pic_url_hd,
  } = data;

  return (
    <div className="profile-summary fade-in">
      <img src={profile_pic_url_hd} alt="avatar" className="avatar" />
      <h3>@{username}</h3>
      <p className="full-name">{full_name}</p>
      <p className="bio">{bio}</p>
      <div className="stats">
        <span>👥 {followers_count} followers</span>
        <span>🔗 {following_count} following</span>
      </div>
    </div>
  );
};

export default ProfileSummary;
