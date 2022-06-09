interface KemonoAPI {
  favorites: KemonoAPI.Favorites,
  posts: KemonoAPI.Posts
  api: KemonoAPI.API
}

namespace KemonoAPI {

  interface Post {
    id: string
    service: string
    title: string
    user: string
    added: string
    published: string
    attachments: string[]
    content: string
    edited: null
    embed: {}
    file: {}
    shared_file: boolean
    faved_seq?: number
  }

  interface Artist {
    id: string
    name: string
    service: string
    indexed: string
    updated: string
    faved_seq?: number
  }

  interface Favorites {
    retrieveFavoriteArtists: () => Promise<string>,
    favoriteArtist: (service: string, id: string) => Promise<boolean>,
    unfavoriteArtist: (service: string, id: string) => Promise<boolean>,
    retrieveFavoritePosts: () => Promise<string>,
    favoritePost: (service: string, user: string, post_id: string) => Promise<boolean>,
    unfavoritePost: (service: string, user: string, post_id: string) => Promise<boolean>
  }

  namespace Favorites {
    interface User extends KemonoAPI.Artist {
    }

    interface Post {
      id: string
      service: string
      user: string
    }
  }

  interface Posts {
    attemptFlag: (service: string, user: string, post_id: string) => Promise<boolean>
  }

  interface API {
    bans: () => Promise<API.BanItem[]>
    bannedArtist: (id:string, service:string) => Promise<API.BannedArtist>
    creators: () => Promise<Artist[]>
    artists: (page?: number, service?: string, name?: string) => Promise<Artist[]>
    logs: (importID: string) => Promise<API.LogItem[]>
  }

  namespace API {
    interface BanItem {
      id: string
      service: string
    }

    interface BannedArtist {
      name: string
    }

    interface LogItem {}
  }
}

namespace Component {
  interface Callback {
    (props: Props): HTMLElement
  }

  /**
   * Init the element off the DOM element.
   */
  interface InitFromElement {
    (props: Props): HTMLElement
  }

  /**
   * Create element through component factory.
   */
  interface InitFromScratch {
    (props: Props): HTMLElement
  }

  interface Props {
    /**
     * Element to initiate the component from.
     */
    element?: HTMLElement
    className?: string
  }

  namespace GlobalNavigation {
    namespace Item {
      interface Callback {
        (props: Props): HTMLLIElement
      }

      interface Props extends Component.Props {
        element?: HTMLLIElement
        link: string
        text?: string
      }

      interface InitFromScratch {
        (props: Props): HTMLElement
      }
    }
  }
}

namespace Events {
  interface Click {
    (event: MouseEvent): void
  }

  interface NavClick {
    (event: NavClickEvent): void
  }

  interface NavClickEvent extends MouseEvent {
    target: HTMLButtonElement
  }
}
