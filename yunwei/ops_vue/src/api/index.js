/** 
 * api接口的统一出口
 */
// 文章模块接口
import globalData from '@/api/globalData.js';
import homePage from '@/api/home/home';
import sidebarapi from '@/api/sidebarapi';
import hostManageApi from '@/api/hostmanage/hostmanage';
import script from '@/api/hostmanage/script';
import fileDistribution from '@/api/hostmanage/fileDistribution.js';
import monitor from '@/api/monitor/monitor';
import getChartData from '@/api/monitor/getChartData';
import appReuqestData from '@/api/monitor/appReuqest';
import faq from '@/api/faq/Faq.js';
import rec from '@/api/rec/Rec.js';
import operationlog from '@/api/operationlog/operationlog.js';
import intelligentCapture from "@/api/diagnose/intelligentCapture";
import version from "@/api/version/version";
import intelligentWireshark from "@/api/diagnose/intelligentWireshark"
import conferenceTopology from "@/api/diagnose/conferenceTopology"
import problemTrack from "@/api/problemtrack/problemTrack.js"
import report from "@/api/report/report.js";
import terminalDiagnosis from '@/api/diagnose/terminalDiagnosis'

// 其他模块的接口……

// 导出接口
export default {
  globalData,
  homePage,
  sidebarapi,
  hostManageApi,
  script,
  fileDistribution,
  monitor,
  getChartData,
  appReuqestData,
  faq,
  rec,
  operationlog,
  intelligentCapture,
  version,
  intelligentWireshark,
  conferenceTopology,
  problemTrack,
  report,
  terminalDiagnosis,
}
