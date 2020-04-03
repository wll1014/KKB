import homePage from '@/api/home/home';

const state = {
  loginInfo: null, //用户登录信息
  siderbarCollapseStatu: true,  //侧边栏展开收起状态
  activeRouteList: '', //当前激活（高亮）的侧边栏
  opsPlatformDomain: null, //平台域
  opsUserDomain: null, //用户域
}

const mutations = {
  login(store, info) {
    store.loginInfo = info
  },
  toggel(store, flag) {
    store.siderbarCollapseStatu = flag;
  },
  activeRouteChange(store, routeList) {
    store.activeRouteList = routeList;
  },
  setOpsPlatformDomain(store, domainList) {
    store.opsPlatformDomain = domainList;
  },
  setOpsUserDomain(store, domainList) {
    store.opsUserDomain = domainList;
  },
}

const actions = {
  login({commit}, info) {
    commit('login', info)
  },
  toggel({commit}, flag) {
    commit('toggel', flag)
  },
  activeRouteChange({commit}, routeList) {
    commit('activeRouteChange', routeList)
  },
  setOpsPlatformDomain({commit}, domainList) {
    commit('setOpsPlatformDomain', domainList)
  },
  setOpsUserDomain({commit}, domainList) {
    commit('setOpsUserDomain', domainList)
  },
}

const getters = {
  getLoginInfo: state => state.loginInfo,
  getsiderbarCollapseStatu: state => state.siderbarCollapseStatu,
  getactiveRouteList: state => state.activeRouteList,
  opsPlatformDomain: state => state.opsPlatformDomain,
  opsUserDomain: state => state.opsUserDomain,
}

export default {
  state,
  mutations,
  getters,
  actions
}
