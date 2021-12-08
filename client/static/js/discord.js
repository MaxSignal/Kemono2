let currentChannel;
//image file formats which can be rendered in browser
let imageFormats = ['bmp', 'gif', 'ico', 'jpeg', 'jpe', 'jpg', 'jfif', 'apng', 'png', 'tga', 'tiff', 'tif', 'svg', 'webp']
/* eslint-disable no-unused-vars */
const loadMessages = async (channelId, skip = 0) => {
  const messages = document.getElementById('messages');
  const loadButton = document.getElementById('load-more-button');
  if (loadButton) {
    loadButton.outerHTML = '';
  }
  if (currentChannel !== channelId) messages.innerHTML = '';
  currentChannel = channelId;
  const channelData = await fetch(`/api/discord/channel/${channelId}?skip=${skip}`);
  const channel = await channelData.json();
  channel.map(msg => {
    let dls = '';
    let avatarurl = '';
    let embeds = '';
    if (msg.content) {
      msg.content = msg.content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/"/g, '&quot;')
        .replace(/<br \/>/g, "");
      let emojis = msg.content.match(/<:.+?:\d+>/g);
      if (emojis) {
        emojis.forEach(emoji => {
          var emoji_code = emoji.match(/\d+/g)[0];
          msg.content = msg.content.replace(emoji, `<img class="emoji" src="https://cdn.discordapp.com/emojis/${emoji_code}">`);
        });
      }
    }
    msg.attachments.map(dl => {
      if (imageFormats.includes(dl.name.split('.').pop())) {
        dls += `<a href="${dl.path}" target="_blank"><img class="user-post-image" style="max-width:300px" src="/thumbnail${dl.path}" onerror="this.src='${dl.path}'"></a><br>`;
      } else {
        dls += `<a href="${dl.path}">Download ${dl.name.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;')}</a><br>`;
      }
    });
    msg.embeds.map(embed => {
      embeds += `
        <a href="${embed.url}" target="_blank">
          <div class="embed-view" style="max-width:300px">
            <p>${(embed.description || embed.title || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;')}</p>
          </div>
        </a>
      `;
    });
    if (msg.author.avatar) {
      avatarurl = `https://cdn.discordapp.com/avatars/${msg.author.id}/${msg.author.avatar}`;
    } else {
      avatarurl = 'https://discordapp.com/assets/1cbd08c76f8af6dddce02c5138971129.png';
    }
    messages.innerHTML = `
      <div class="message">
        <div class="avatar" style="background-image:url('${avatarurl}')"></div>
        <div style="display:inline-block">
          <div class="message-header">
            <b><p>${msg.author.username.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;')}</p></b>
            <p style="color:#757575">${msg.published}</p>
          </div>
          <p><pre class="message__body">${msg.content}</pre></p>
          ${dls}
          ${embeds}
        </div>
      </div>
    ` + messages.innerHTML;
  });
  messages.innerHTML = `
    <div class="message" id="load-more-button">
      <button onClick="loadMessages('${channelId}', ${skip + 10})" class="load-more-button">
        Load More
      </button>
    </div>
  ` + messages.innerHTML;
};
/* eslint-enable no-unused-vars */

const load = async () => {
  const pathname = window.location.pathname.split('/');
  const serverData = await fetch(`/api/discord/channels/lookup?q=${pathname[3]}`);
  const server = await serverData.json();
  const channels = document.getElementById('channels');
  server.forEach(ch => {
    const channel = document.getElementById(`channel-${ch.id}`);
    if (!channel) {
      channels.innerHTML += `
        <div class="channel" id="channel-${ch.id}" onClick="loadMessages('${ch.id}')">
          <p>#${ch.name.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;')}</p>
        </div>
      `;
    }
  });
};

load();
