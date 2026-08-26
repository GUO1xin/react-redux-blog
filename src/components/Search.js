import ArticleList from './ArticleList';
import React from 'react';
import agent from '../agent';
import { connect } from 'react-redux';
import {
  SEARCH_PAGE_LOADED,
  SEARCH_PAGE_UNLOADED
} from '../constants/actionTypes';

const mapStateToProps = state => ({
  ...state.articleList
});

const mapDispatchToProps = dispatch => ({
  onLoad: (pager, payload, query) =>
    dispatch({ type: SEARCH_PAGE_LOADED, pager, payload, query }),
  onUnload: () =>
    dispatch({ type: SEARCH_PAGE_UNLOADED })
});

class Search extends React.Component {
  loadResults(query) {
    const keyword = decodeURIComponent(query);
    this.props.onLoad(
      page => agent.Articles.search(keyword, page),
      agent.Articles.search(keyword),
      keyword
    );
  }

  componentWillMount() {
    this.loadResults(this.props.match.params.query);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.match.params.query !== this.props.match.params.query) {
      this.loadResults(nextProps.match.params.query);
    }
  }

  componentWillUnmount() {
    this.props.onUnload();
  }

  render() {
    return (
      <div className="home-page">
        <div className="container page">
          <div className="row">
            <div className="col-md-12">
              <p>搜索“{this.props.query}”的结果，共 {this.props.articlesCount || 0} 篇</p>
              <ArticleList
                pager={this.props.pager}
                articles={this.props.articles}
                articlesCount={this.props.articlesCount}
                currentPage={this.props.currentPage} />
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(Search);
