// ping user-канала (presence)
const wsProto = location.protocol === "https:" ? "wss" : "ws";
const wsUser = new WebSocket(`${wsProto}://${location.host}/ws/user/`);
wsUser.onopen = () => setInterval(() => {
  if (wsUser.readyState === 1) wsUser.send(JSON.stringify({type:"heartbeat"}));
}, 20000);

wsUser.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === "notify" && typeof toast === "function") {
    toast(msg.text);
  }
};

// Командная комната
(function connectTeam(teamId){
  const ws = new WebSocket(`${wsProto}://${location.host}/ws/team/${teamId}/`);

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (["created","updated","deleted"].includes(msg.action)){
      if (typeof loadTasks === "function") loadTasks();
    }
  };

  ws.onclose = () => setTimeout(() => connectTeam(teamId), 1000);
})(window.TEAM_ID);

