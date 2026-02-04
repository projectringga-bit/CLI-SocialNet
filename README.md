# CLI SocialNet

![CLI-SocialNet](./CLI-SocialNet.png)

A terminal-based social networking platform written in Python. Connect, share, and interact with users through a command-line interface.

> _This project was inspired by Twitter (X) and Mastodon_

> _This project mainly served as a learning experience for SQL-based databases (this was my main goal, yeah)_

## Table of Contents

- [Features](#features)
- [Commands Reference](#commands-reference)
- [Requirements](#requirements)
- [Installation](#installation-or-you-can-use-the-exe-release)
- [Directory Tree](#directory-tree)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [Database Support](#database-support)
- [XP and Achievements System](#xp-and-achievements-system)
- [Admin Commands](#admin-commands)
- [Settings and Aliases](#settings-and-aliases)
- [AI Usage](#ai-usage)
- [License](#license)

## Features

- **Posts & Content:** Create text posts, image posts (converted to ASCII art), poll posts, and quote other posts.
- **Interactions:** Like, comment, repost, pin and bookmark posts
- **Social Features:** Follow/unfollow users, view profiles, and explore their profiles.
- **Direct Messages:** Send and receive DMs with other users.
- **Notifications:** Get notified about interactions and mentions.
- **Hashtags & Mentions:** Use hashtags and mention other users in posts.
- **Search:** Search for posts, users, hashtags and mentions.
- **ASCII Art Conversion:** Convert images to ASCII art for terminal display (posts and avatars).
- **Big Texts:** Create large text posts using ASCII art.
- **Polls:** Create and participate in polls posts.
- **Pinned and Bookmarked Posts:** Pin important posts to your profile and bookmark posts.
- **Private Accounts:** Set your account to private mode.
- **User Profiles:** customize your profile with display name, avatar, bio, status, location and website (+ pinned posts).
- **XP and Levels:** Earn XP for interactions and level up to reach the top of the leaderboard.
- **Admin Features:** Moderate content and manage users with admin privileges (account).

## Commands Reference

### Account:
| Command | Description | Usage |
|---------|-------------|-------|
| register | Create a new account | `register <username>` |
| login | Login to your account | `login <username>` |
| logout | Logout from your account | `logout` |
| whoami | Show currently logged in user | `whoami` |
| deleteaccount | Delete your account permanently | `deleteaccount` |
| changepassword | Change your password | `changepassword` |

### Discovery:
| Command | Description | Usage |
|---------|-------------|-------|
| home | View home feed | `home` |
| feed | View feed from followed users | `feed [page]` |
| explore | View global feed | `explore [page]` |
| search | Search posts | `search <query> [page]` |
| usersearch | Search users | `usersearch <query> [page]` |
| hashtag | View posts with hashtag | `hashtag <hashtag> [page]` |
| htrending | View trending hashtags | `htrending` |
| hsearch | Search hashtags | `hsearch <query> [page]` |
| mentions | View user mentions | `mentions <username> [page]` |

### Posts and Content:
| Command | Description | Usage |
|---------|-------------|-------|
| post | Create a text post | `post <content>` |
| postimg | Create post with local image | `postimg <path> [caption]` |
| posturl | Create post with image from URL | `posturl <url> [caption]` |
| postbig | Create post with large ASCII text | `postbig <text> [content]` |
| postpoll | Create a poll | `postpoll <question> \| <?> \| <opt1> \| <opt2>...` |
| viewpost | View a specific post | `viewpost <post_id>` |
| deletepost | Delete your post | `deletepost <post_id>` |
| myposts | View all your posts | `myposts` |

### Interactions:
| Command | Description | Usage |
|---------|-------------|-------|
| like | Like a post (+2 XP) | `like <post_id>` |
| unlike | Remove your like | `unlike <post_id>` |
| likes | View who liked a post | `likes <post_id>` |
| comment | Comment on a post (+5 XP) | `comment <post_id> <comment_text>` |
| delcomment | Delete your comment | `delcomment <comment_id>` |
| comments | View post comments | `comments <post_id>` |
| repost | Repost to your timeline (+5 XP) | `repost <post_id>` |
| unrepost | Remove your repost | `unrepost <post_id>` |
| quote | Quote a post with commentary | `quote <post_id> <comment>` |
| reposts | View who reposted | `reposts <post_id>` |

### Social:
| Command | Description | Usage |
|---------|-------------|-------|
| follow | Follow a user (+5 XP) | `follow <username>` |
| unfollow | Unfollow a user | `unfollow <username>` |
| followers | View followers | `followers [username]` |
| following | View who you follow | `following [username]` |
| profile | View user profile | `profile [username]` |
| dm | Send direct message | `dm <username> <message>` |
| inbox | View your inbox | `inbox` |
| messages | View conversation | `messages <username>` |
| closedm | Close conversation | `closedm <username>` |

### Profile Customization:
| Command | Description | Usage |
|---------|-------------|-------|
| displayname | Set display name | `displayname <new_display_name>` |
| bio | Set biography | `bio <new_bio>` |
| status | Set status message | `status <new_status>` |
| location | Set location | `location <new_location>` |
| website | Set website URL | `website <new_website>` |
| avatar | Set avatar from local image | `avatar <image_path>` |
| avatarurl | Set avatar from URL | `avatarurl <image_url>` |
| removeavatar | Remove your avatar | `removeavatar` |
| private | Toggle private account | `private` |

### Polls:
| Command | Description | Usage |
|---------|-------------|-------|
| votepoll | Vote in a poll | `votepoll <poll_id> <option_num>` |
| mypolls | View your polls | `mypolls [page]` |

### Pins and Bookmarks:
| Command | Description | Usage |
|---------|-------------|-------|
| pin | Pin a post to profile | `pin <post_id>` |
| unpin | Unpin a post | `unpin <post_id>` |
| pinned | View pinned posts | `pinned [username]` |
| bookmark | Save post for later | `bookmark <post_id>` |
| unbookmark | Remove bookmark | `unbookmark <post_id>` |
| bookmarks | View your bookmarks | `bookmarks` |

### XP and Achievements:
| Command | Description | Usage |
|---------|-------------|-------|
| xp | View your XP and level | `xp` |
| achievements | View all achievements | `achievements` |
| leaderboard | View top players | `leaderboard [limit]` |

### Reports:
| report | Report a post | `report <post/comment/user> <id/user> <reason>` |

### Notifications and Settings:
| Command | Description | Usage |
|---------|-------------|-------|
| notifications | View notifications | `notifications` |
| clearn | Clear notifications | `clearn` |
| settings | View current settings | `settings` |
| setting | Change a setting | `setting <setting_name> <new_value>` |

### Utilities:
| Command | Description | Usage |
|---------|-------------|-------|
| help | Show help message | `help` |
| exit / quit | Exit application | `exit` / `quit` |
| clear | Clear console | `clear` |
| alias | Create command alias | `alias [alias] [command]` |
| unalias | Remove alias | `unalias <alias>` |
| bigtext | Preview ASCII text | `bigtext <big_content>` |

## Requirements
- **Python**: 3.7 or higher
- **Dependencies**: Install via `requirements.txt`
    - Pillow
    - pymongo

## Installation (or you can use the .exe release)
1. **Clone the repository** and navigate to the project folder:
    ```bash
    git clone https://github.com/artur3333/CLI-SocialNet.git
    cd CLI-SocialNet
    ```

2. **Install the required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

## Directory Tree
```
CLI-SocialNet/
├── main.py              # Main application entry point
├── config.json          # Configuration settings
├── config_loader.py     # Configuration loader
├── auth.py              # Authentication & session management
├── db.py                # Database abstraction layer
├── database_s.py        # SQLite
├── database_m.py        # MongoDB
├── posts.py             # Post creation & management
├── social.py            # Social features (follow, profile, dm)
├── admin.py             # Admin & moderation features
├── level.py             # XP, levels & achievements
├── ascii.py             # ASCII art conversion
├── utils.py             # Utility functions & helpers
└── __init__.py          # Package initializer
```

## Configuration

The application uses a `config.json` file for configuration. On first run, a default configuration file will be automatically created if it doesn't exist.

Edit `config.json` to customize your installation:

```json
{
    "DATABASE": "sqlite",
    "SQL_PATH": "socialnet.db",
    "MONGODB_URI": "mongodb://localhost:27017/",
    "MONGODB_NAME": "socialnet",
    "ENABLE_REGISTRATION_LIMIT": true,
    "DEFAULT_ADMIN_PASSWORD": "admin123"
}
```

## Getting Started

1. **Start the application**:
   ```bash
   python main.py
   ```

2. **Register a new user**:
   ```
   register <username>
   ```
   You'll be prompted to enter a password.

3. **Login**:
   ```
   login <username>
   ```

4. **View available commands**:
   ```
   help
   ```

5. **You can login as an admin user** with the username `admin` and the default password set in `config.json`. Admins have access to additional moderation commands.

## Database Support

### SQLite (Default)
- No additional setup required
- Stores data in `socialnet.db` file

### MongoDB (Optional)
- Requires MongoDB server installation

**Switching to MongoDB:**
1. Install MongoDB
2. Update `config.json`:
   ```json
   {
       "DATABASE": "mongodb",
       "MONGODB_URI": "mongodb://localhost:27017/"
   }
   ```
3. Restart the application

## XP and Achievements System

Earn XP for various activities:
- Create a post: **+10 XP**
- Comment: **+5 XP**
- Like a post: **+2 XP**
- Repost: **+5 XP**
- Follow someone: **+5 XP**

or compleate achievements to gain bonus XP

## Admin Commands

```bash
admin                             # View dashboard
admin ban  [reason]               # Ban a user
admin unban                       # Unban a user
admin deletepost                  # Delete any post
admin makeadmin                   # Grant admin rights
admin removeadmin                 # Remove admin rights
admin verify                      # Verify a user
admin unverify                    # Remove verification
admin reports [status] [page]     # View reports
admin resolve                     # Resolve a report
admin dismiss                     # Dismiss a report
admin logs [page]                 # View admin action logs
```

## Settings and Aliases

### Settings Customization

Users can customize their experience:
- **Color Scheme**: Personalize colors
- **Terminal Width**: Adjust display width
- **Posts per Page**: Customize posts shown per page
- **Notifications**: Configure notification preferences

Access settings with:
```bash
settings                                # View all settings
setting <setting_name> <new_value>      # Change a setting
```

### Command Aliases
Create your own command shortcuts for existing commands:
```bash
alias [alias] [command]      # Create an alias
unalias <alias>              # Remove an alias
```

## AI Usage
This project was developed with selective use of AI assistance. Most of the implementation was done independently, with AI mainly used for:

**MongoDB Implementation (`database_m.py`)**
- AI was used extensively to help implement the **MongoDB backend** to speed up the implementation process
- Primary focus was on fixing compatibility issues and bugs.
- Significant use of tab autocomplete (code suggestions)

**UI and Layout (`utils.py` formatting)**
- AI assistance was used to help with text wrapping, Unicode alignment and helped debug border rendering in the display UI system

**Bug Fixing and Debugging**
- AI was consulted when facing difficult bugs, particularly in:
  - Comment system implementation
  - Database issues
  - Alignment and formatting problems
  - Other bugs

**Documentation**
- This README was partially generated by AI and then modified to ensure accuracy.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details
