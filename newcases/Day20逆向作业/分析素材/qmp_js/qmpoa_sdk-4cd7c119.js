const u=`.qmp-one-chat-btn {
  position: fixed;
  z-index: 9999999999;
  background-color: red;
  width: 60px;
  height: 60px;
  bottom: 40px;
  right: 20px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: rgba(73, 90, 255, 0.3) 0px 0px 20px 4px;
  background: linear-gradient(115deg, rgb(73, 90, 255), rgb(10, 207, 254)) white;
  cursor: pointer;
}
.qmp-one-chat-btn .btn-icon-send {
  width: 30px;
  color: #fff;
}
.qmp-one-chat-btn #one-chat-unread {
  background-color:#f56c6c;
  position: absolute;
  min-width: 18px;
  text-align: center;
  height: 18px;
  /* background: red; */
  border-radius: 9px;
  right: -4px;
  top: -4px;
  box-sizing: border-box;
  font-size: 12px;
  line-height: 18px;
  color: white;
  padding: 0 5px;
  display: none;
}
#one-chat-unread.is-show {
  display: block;
}
.qmp-one-chat-iframe {
  border: none;
  width: 430px;
  max-height: 600px;
  z-index: -999;
  height: 100%;
  position: fixed;
  right: 0;
  overflow: hidden;
  bottom: 0;
  border-radius: 8px;
  display: none;
  pointer-events: none;
}
.qmp-one-chat-iframe.is-mobile {
  width: 100vw;
}
`,f=async()=>{const e=document.createElement("div"),t=document.createElement("style");return t.innerHTML=u,e.className="qmp-one-chat-btn",e.style.visibility="hidden",e.setAttribute("title","咨询客服"),e.innerHTML=`
    <span id="one-chat-unread"></span>
    <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" class="btn-icon-send">
      <path fill="currentColor" d="m174.72 855.68 135.296-45.12 23.68 11.84C388.096 849.536 448.576 864 512 864c211.84 0 384-166.784 384-352S723.84 160 512 160 128 326.784 128 512c0 69.12 24.96 139.264 70.848 199.232l22.08 28.8-46.272 115.584zm-45.248 82.56A32 32 0 0 1 89.6 896l58.368-145.92C94.72 680.32 64 596.864 64 512 64 299.904 256 96 512 96s448 203.904 448 416-192 416-448 416a461.056 461.056 0 0 1-206.912-48.384l-175.616 58.56z"></path>
      <path fill="currentColor" d="M512 563.2a51.2 51.2 0 1 1 0-102.4 51.2 51.2 0 0 1 0 102.4zm192 0a51.2 51.2 0 1 1 0-102.4 51.2 51.2 0 0 1 0 102.4zm-384 0a51.2 51.2 0 1 1 0-102.4 51.2 51.2 0 0 1 0 102.4z"></path>
    </svg>
  `,document.body.append(t),document.body.append(e),e};function w(e){return Object.entries(e).map(([t,n])=>`${t}=${n}`).join("&")}function b(e){localStorage.setItem("one-chat-user-uuid",e)}function g(){return localStorage.getItem("one-chat-user-uuid")||""}function v(){return["iphone","ipod","ipad","android","mobile","blackberry","webos","incognito","webmate","bada","nokia","lg","ucweb","skyfire"].some(e=>navigator.userAgent.toLowerCase().indexOf(e)!==-1)}let h,l,r=!1;function I(e=""){r||(l=document.title),r=!0,document.title=`【新消息】${e}`,clearInterval(h);let t=!1;h=setInterval(()=>{document.title=t?`【新消息】${e}`:"",t=!t},1e3)}function d(){r&&(clearInterval(h),l&&(document.title=l),r=!1)}const i={domain:JSON.parse('{"name":"qtable","value":"qtable","domain_socket":"wss://oneapi.qmpoa.com","api":"https://oneapi.qmpoa.com","domain":"https://chat.qmpoa.com"}').domain,chatBtn:null,chatIframe:null,isActiveChat:!1,imWindow:null,imWindowVisible:!1,checkCloseTimer:void 0,unreadNum:0,channelInfo:{src:""},removeMessageEvent:null,async initChatBtn(){this.chatBtn=await f();try{const e=sessionStorage.getItem("one-chat-channel");this.channelInfo=e?JSON.parse(e):{}}catch(e){console.log(e)}this.chatIframe=await this.createChatIframe(),this.chatBtn.addEventListener("click",this.openChat.bind(this))},getChatUrl(){const e=w({origin:encodeURIComponent(location.origin),userUUID:g(),...this.channelInfo});return console.log("chat url",e),`${this.domain}?${e}`},async createChatIframe(){return new Promise(e=>{const t=document.createElement("iframe");t.classList.add("qmp-one-chat-iframe"),v()&&t.classList.add("is-mobile"),t.style.visibility="hidden",t.style.zIndex="-1000",t.src=this.getChatUrl(),console.log({VITE_WSS:"wss://oneapi.qmpoa.com",VITE_DOMAIN:"https://chat.qmpone.com",VITE_API_DOMAIN:"https://oneapi.qmpoa.com",VITE_APP_BRANCH:'{"name":"qtable","value":"qtable","domain_socket":"wss://oneapi.qmpoa.com","api":"https://oneapi.qmpoa.com","domain":"https://chat.qmpoa.com"}',BASE_URL:"/",MODE:"production",DEV:!1,PROD:!0,SSR:!1}),document.body.appendChild(t);const n=()=>{var a;(a=this.chatIframe)==null||a.removeEventListener("load",n),e(t)};t.addEventListener("load",n);const s=this.onReceiveMessage.bind(this);window.addEventListener("message",s),this.removeMessageEvent=()=>{window.removeEventListener("message",s)}})},onReceiveMessage(e){const{type:t,payload:n}=e.data;switch(console.log("host onMessage",t,n,e.source===window),t){case"chat:close":this.closeChat();break;case"user:update":C(n);break;case"message":this.imWindowVisible||(I(n),this.setUnreadNum(this.unreadNum+1));break;case"showChatBtn":this.showChatBtn();break;case"destroy":this.destroy();break;case"imWindowVisibleChange":this.imWindowVisible=n,n&&(d(),this.setUnreadNum(0));break}},postMessage(e){var t,n;(n=(t=this.chatIframe)==null?void 0:t.contentWindow)==null||n.postMessage(e,this.domain)},async openChat(){this.imWindow?this.imWindow.focus():this.openImWindow(),this.isActiveChat=!0,this.chatIframe&&(this.chatIframe.style.visibility="visible",this.chatIframe.style.zIndex="9999999"),d(),this.setUnreadNum(0),setTimeout(()=>{this.postMessage({type:"chat:open"})})},openImWindow(e=720,t=650){const n=window.screen.width,s=window.screen.height,a=(n-e)/2,p=(s-t)/2;let o=sessionStorage.getItem("imWindowName")||"";o||(o=Date.now()+"",sessionStorage.setItem("imWindowName",o));const c=window.open(this.getChatUrl(),o,`width=${e},height=${t},left=${a},top=${p},resizable=yes,scrollbars=yes`);c&&(this.imWindow=c,this.imWindowVisible=!0,clearInterval(this.checkCloseTimer),this.checkCloseTimer=setInterval(()=>{(!c||c.closed)&&(clearInterval(this.checkCloseTimer),console.log("im window close"),this.closeChat())},1e3))},closeChat(){this.imWindow=null,this.imWindowVisible=!1,this.chatIframe&&(this.isActiveChat=!1,this.chatBtn.style.display="flex",this.chatIframe.style.visibility="hidden",this.chatIframe.style.zIndex="-1000",this.postMessage({type:"chat:close"}))},setUnreadNum(e){const t=e>99?"+99":e.toString(),n=document.getElementById("one-chat-unread");n==null||n.classList.remove("is-show"),e&&(n==null||n.classList.add("is-show"),n.innerHTML=t),this.unreadNum=e},showChatBtn(){this.chatBtn&&(this.chatBtn.style.visibility="visible")},destroy(){this.unreadNum=0,this.chatIframe&&document.body.removeChild(this.chatIframe),this.chatBtn&&document.body.removeChild(this.chatBtn),this.chatIframe=null,this.chatBtn=null,this.isActiveChat=!1,this.removeMessageEvent&&this.removeMessageEvent(),this.removeMessageEvent=null}};function y(){window.oneChatApi={destroy(){i.destroy()},init(){document.querySelector(".qmp-one-chat-btn")||i.initChatBtn()},showChatBtn(){i.showChatBtn()}}}function C(e){b(e),i.postMessage({type:"user:update",payload:e}),!e&&i.chatIframe&&(i.chatIframe.remove(),i.initChatBtn())}function m(){i.initChatBtn(),y()}document?m():window.addEventListener("load",m);
