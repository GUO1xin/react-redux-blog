import React from 'react';

const Banner = ({ appName, token }) => {
  if (token) {
    return null;
  }
  return (
    <div className="banner">
      <div className="container">
        <h1 className="logo-font">
          {appName.toLowerCase()}
        </h1>
        <p>一个分享你的知识的地方。</p>
      </div>
    </div>
  );
};

export default Banner;
